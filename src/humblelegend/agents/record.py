"""
记录Agent
处理所有记录类操作：日常记录、热量估算、内容收藏、文本润色
"""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from loguru import logger

from ..core.database import init_database
from ..core.config import Config
from .parser import ParsedCommand, IntentType
from .calorie import CalorieAgent
from .polish import PolishAgent
from .collect import CollectAgent


@dataclass
class RecordResult:
    success: bool
    message: str
    record_id: Optional[int] = None
    record_type: Optional[str] = None
    content: Optional[str] = None
    topics: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    needs_confirmation: bool = True
    timestamp: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "record_id": self.record_id,
            "record_type": self.record_type,
            "content": self.content,
            "topics": self.topics,
            "metadata": self.metadata,
            "needs_confirmation": self.needs_confirmation,
            "timestamp": self.timestamp,
        }


class RecordAgent:
    def __init__(self, config: Config, db_path: str = "data/database.db"):
        self.config = config
        self.db_path = db_path
        init_database(db_path)
        
        self.calorie_agent = CalorieAgent(config)
        self.polish_agent = PolishAgent(config)
        self.collect_agent = CollectAgent(config)
    
    def execute(self, command: ParsedCommand, user_id: str = "default_user") -> RecordResult:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if command.intent == IntentType.RECORD_DAILY:
            return self._record_daily(command, user_id, timestamp)
        elif command.intent == IntentType.RECORD_CALORIE:
            return self._record_calorie(command, user_id, timestamp)
        elif command.intent == IntentType.COLLECT:
            return self._record_collect(command, user_id, timestamp)
        elif command.intent == IntentType.POLISH:
            return self._record_polish(command, user_id, timestamp)
        else:
            return RecordResult(
                success=False,
                message="未知的记录类型",
                needs_confirmation=False,
                timestamp=timestamp,
            )
    
    def _record_daily(self, command: ParsedCommand, user_id: str, timestamp: str) -> RecordResult:
        content = command.content
        if not content:
            return RecordResult(
                success=False,
                message="请提供要记录的内容",
                needs_confirmation=False,
                timestamp=timestamp,
            )
        
        topics = self._suggest_topics(content)
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (user_id,)
        )
        
        cursor.execute(
            """INSERT INTO records 
               (user_id, record_type, content, topics, timestamp, confirmed)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, "daily", content, json.dumps(topics, ensure_ascii=False), timestamp, False)
        )
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self._increment_session_count(user_id)
        
        message = self._generate_confirmation_message("daily", content, topics, timestamp)
        
        return RecordResult(
            success=True,
            message=message,
            record_id=record_id,
            record_type="daily",
            content=content,
            topics=topics,
            needs_confirmation=True,
            timestamp=timestamp,
        )
    
    def _record_calorie(self, command: ParsedCommand, user_id: str, timestamp: str) -> RecordResult:
        content = command.content
        images = [a for a in command.attachments if a.get("type") == "image"]
        
        calorie_result = self.calorie_agent.estimate(content, images)
        
        if not calorie_result.get("success"):
            return RecordResult(
                success=False,
                message=calorie_result.get("message", "热量估算失败"),
                needs_confirmation=False,
                timestamp=timestamp,
            )
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (user_id,)
        )
        
        topics = ["饮食作息"]
        cursor.execute(
            """INSERT INTO records 
               (user_id, record_type, content, topics, metadata, timestamp, confirmed)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, "calorie", content, json.dumps(topics, ensure_ascii=False), 
             json.dumps(calorie_result, ensure_ascii=False), timestamp, False)
        )
        
        record_id = cursor.lastrowid
        
        cursor.execute(
            """INSERT INTO calorie_records 
               (record_id, food_name, calories, protein, fat, carbs, sodium, estimated_weight)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (record_id, calorie_result.get("food_name", "未知食物"),
             calorie_result.get("calories", 0), calorie_result.get("protein", 0),
             calorie_result.get("fat", 0), calorie_result.get("carbs", 0),
             calorie_result.get("sodium", 0), calorie_result.get("estimated_weight", 0))
        )
        
        conn.commit()
        conn.close()
        
        self._increment_session_count(user_id)
        
        message = self._generate_calorie_confirmation(calorie_result, timestamp)
        
        return RecordResult(
            success=True,
            message=message,
            record_id=record_id,
            record_type="calorie",
            content=content,
            topics=topics,
            metadata=calorie_result,
            needs_confirmation=True,
            timestamp=timestamp,
        )
    
    def _record_collect(self, command: ParsedCommand, user_id: str, timestamp: str) -> RecordResult:
        content = command.content
        attachments = command.attachments
        
        collect_result = self.collect_agent.collect(content, attachments, user_id)
        
        if not collect_result.get("success"):
            return RecordResult(
                success=False,
                message=collect_result.get("message", "收藏失败"),
                needs_confirmation=False,
                timestamp=timestamp,
            )
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (user_id,)
        )
        
        topics = self._suggest_topics(content)
        cursor.execute(
            """INSERT INTO records 
               (user_id, record_type, content, topics, metadata, timestamp, confirmed)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, "collect", content, json.dumps(topics, ensure_ascii=False),
             json.dumps(collect_result, ensure_ascii=False), timestamp, False)
        )
        
        record_id = cursor.lastrowid
        
        cursor.execute(
            """INSERT INTO collections 
               (record_id, content_type, content_hash, storage_path, url)
               VALUES (?, ?, ?, ?, ?)""",
            (record_id, collect_result.get("content_type", "text"),
             collect_result.get("content_hash", ""),
             collect_result.get("storage_path"),
             collect_result.get("url"))
        )
        
        conn.commit()
        conn.close()
        
        self._increment_session_count(user_id)
        
        message = self._generate_collect_confirmation(collect_result, timestamp)
        
        return RecordResult(
            success=True,
            message=message,
            record_id=record_id,
            record_type="collect",
            content=content,
            topics=topics,
            metadata=collect_result,
            needs_confirmation=True,
            timestamp=timestamp,
        )
    
    def _record_polish(self, command: ParsedCommand, user_id: str, timestamp: str) -> RecordResult:
        content = command.content
        style = command.params.get("style", "默认")
        
        if not content:
            return RecordResult(
                success=False,
                message="请提供要润色的文本内容",
                needs_confirmation=False,
                timestamp=timestamp,
            )
        
        polish_result = self.polish_agent.polish(content, style)
        
        if not polish_result.get("success"):
            return RecordResult(
                success=False,
                message=polish_result.get("message", "润色失败"),
                needs_confirmation=False,
                timestamp=timestamp,
            )
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (user_id,)
        )
        
        topics = []
        cursor.execute(
            """INSERT INTO records 
               (user_id, record_type, content, topics, metadata, timestamp, confirmed)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, "polish", content, json.dumps(topics, ensure_ascii=False),
             json.dumps(polish_result, ensure_ascii=False), timestamp, False)
        )
        
        record_id = cursor.lastrowid
        
        cursor.execute(
            """INSERT INTO polish_records 
               (record_id, original_text, polished_text, style)
               VALUES (?, ?, ?, ?)""",
            (record_id, content, polish_result.get("polished_text", ""), style)
        )
        
        conn.commit()
        conn.close()
        
        self._increment_session_count(user_id)
        
        message = self._generate_polish_confirmation(polish_result, timestamp)
        
        return RecordResult(
            success=True,
            message=message,
            record_id=record_id,
            record_type="polish",
            content=content,
            topics=topics,
            metadata=polish_result,
            needs_confirmation=True,
            timestamp=timestamp,
        )
    
    def confirm_record(self, record_id: int, modifications: Optional[Dict[str, Any]] = None) -> bool:
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if modifications:
            if "content" in modifications:
                cursor.execute(
                    "UPDATE records SET content = ?, confirmed = ? WHERE id = ?",
                    (modifications["content"], True, record_id)
                )
            if "topics" in modifications:
                cursor.execute(
                    "UPDATE records SET topics = ?, confirmed = ? WHERE id = ?",
                    (json.dumps(modifications["topics"], ensure_ascii=False), True, record_id)
                )
        else:
            cursor.execute(
                "UPDATE records SET confirmed = ? WHERE id = ?",
                (True, record_id)
            )
        
        conn.commit()
        conn.close()
        
        logger.info(f"记录已确认: record_id={record_id}")
        return True
    
    def _suggest_topics(self, content: str) -> List[str]:
        topics = []
        content_lower = content.lower()
        
        topic_keywords = {
            "饮食作息": ["吃", "喝", "饭", "菜", "早餐", "午餐", "晚餐", "睡觉", "起床", "运动", "健身"],
            "工作": ["工作", "会议", "项目", "任务", "报告", "面试", "加班", "deadline"],
            "娱乐": ["游戏", "电影", "音乐", "书", "旅游", "逛街", "聚会"],
        }
        
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    if topic not in topics:
                        topics.append(topic)
                    break
        
        return topics if topics else ["日常"]
    
    def _generate_confirmation_message(self, record_type: str, content: str, topics: List[str], timestamp: str) -> str:
        topics_str = "、".join(topics)
        return f"""已记录完成，请确认：

📝 内容：{content}
📅 时间：{timestamp}
🏷️ 主题：{topics_str}

如需修改请回复，确认无误请回复"确认"或直接进行其他操作。"""
    
    def _generate_calorie_confirmation(self, result: Dict[str, Any], timestamp: str) -> str:
        return f"""热量估算完成，请确认：

🍽️ 食物：{result.get('food_name', '未知')}
⚖️ 估算重量：{result.get('estimated_weight', 0)}克
🔥 热量：{result.get('calories', 0)} 千卡
🥩 蛋白质：{result.get('protein', 0)} 克
🧈 脂肪：{result.get('fat', 0)} 克
🍞 碳水：{result.get('carbs', 0)} 克
🧂 钠：{result.get('sodium', 0)} 毫克
📅 时间：{timestamp}

如需修改请回复，确认无误请回复"确认"或直接进行其他操作。"""
    
    def _generate_collect_confirmation(self, result: Dict[str, Any], timestamp: str) -> str:
        content_type_map = {
            "text": "文本",
            "image": "图片",
            "video": "视频",
            "link": "链接",
        }
        content_type = content_type_map.get(result.get("content_type", "text"), "未知")
        
        return f"""收藏完成，请确认：

📦 类型：{content_type}
📄 内容：{result.get('content', '')[:100]}{'...' if len(result.get('content', '')) > 100 else ''}
📅 时间：{timestamp}

如需修改请回复，确认无误请回复"确认"或直接进行其他操作。"""
    
    def _generate_polish_confirmation(self, result: Dict[str, Any], timestamp: str) -> str:
        return f"""润色完成，请确认：

📝 原文：
{result.get('original_text', '')}

✨ 润色后：
{result.get('polished_text', '')}

🎨 风格：{result.get('style', '默认')}
📅 时间：{timestamp}

如需修改请回复，确认无误请回复"确认"或直接进行其他操作。"""
    
    def _increment_session_count(self, user_id: str) -> None:
        import sqlite3
        from datetime import datetime
        
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO sessions (user_id, session_date, command_count)
               VALUES (?, ?, 1)
               ON CONFLICT(user_id, session_date)
               DO UPDATE SET command_count = command_count + 1""",
            (user_id, today)
        )
        
        conn.commit()
        conn.close()
