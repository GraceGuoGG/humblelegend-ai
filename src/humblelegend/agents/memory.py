"""
记忆Agent
记录用户偏好、指令习惯，支持查询与清除
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from loguru import logger

from ..core.config import Config


class MemoryAgent:
    def __init__(self, config: Config, db_path: str = "data/database.db"):
        self.config = config
        self.db_path = db_path
        self._command_shortcuts: Dict[str, str] = {}
        self._topic_preferences: Dict[str, str] = {}
        self._output_preferences: Dict[str, Any] = {}
        self._load_memories()
    
    def _load_memories(self, user_id: str = "default_user") -> None:
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT memory_type, key, value FROM memories WHERE user_id = ?",
            (user_id,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            memory_type, key, value = row
            if memory_type == "command":
                self._command_shortcuts[key] = value
            elif memory_type == "topic":
                self._topic_preferences[key] = value
            elif memory_type == "output":
                self._output_preferences[key] = json.loads(value)
    
    def record_command_shortcut(self, user_id: str, shortcut: str, full_command: str) -> None:
        self._command_shortcuts[shortcut] = full_command
        self._save_memory(user_id, "command", shortcut, full_command)
    
    def record_topic_preference(self, user_id: str, content_pattern: str, topic: str) -> None:
        self._topic_preferences[content_pattern] = topic
        self._save_memory(user_id, "topic", content_pattern, topic)
    
    def record_output_preference(self, user_id: str, preference_type: str, value: Any) -> None:
        self._output_preferences[preference_type] = value
        self._save_memory(user_id, "output", preference_type, json.dumps(value, ensure_ascii=False))
    
    def apply_command_shortcuts(self, user_input: str) -> str:
        for shortcut, full_command in self._command_shortcuts.items():
            if user_input.strip() == shortcut:
                logger.info(f"应用指令缩写: {shortcut} -> {full_command}")
                return full_command
        return user_input
    
    def get_preferred_topic(self, content: str) -> Optional[str]:
        for pattern, topic in self._topic_preferences.items():
            if pattern in content:
                return topic
        return None
    
    def get_output_preference(self, preference_type: str) -> Optional[Any]:
        return self._output_preferences.get(preference_type)
    
    def get_all_memories(self, user_id: str = "default_user") -> Dict[str, Any]:
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM memories WHERE user_id = ?",
            (user_id,)
        )
        total_count = cursor.fetchone()[0]
        
        cursor.execute(
            "SELECT memory_type, COUNT(*) FROM memories WHERE user_id = ? GROUP BY memory_type",
            (user_id,)
        )
        type_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "total_count": total_count,
            "command_shortcuts": len(self._command_shortcuts),
            "topic_preferences": len(self._topic_preferences),
            "output_preferences": len(self._output_preferences),
            "type_counts": type_counts,
            "limit": self.config.memory_limit,
        }
    
    def clear_memories(self, user_id: str, memory_type: Optional[str] = None) -> Dict[str, Any]:
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if memory_type:
            cursor.execute(
                "DELETE FROM memories WHERE user_id = ? AND memory_type = ?",
                (user_id, memory_type)
            )
            
            if memory_type == "command":
                self._command_shortcuts.clear()
            elif memory_type == "topic":
                self._topic_preferences.clear()
            elif memory_type == "output":
                self._output_preferences.clear()
        else:
            cursor.execute("DELETE FROM memories WHERE user_id = ?", (user_id,))
            self._command_shortcuts.clear()
            self._topic_preferences.clear()
            self._output_preferences.clear()
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"已清除记忆: user={user_id}, type={memory_type}, count={deleted_count}")
        
        return {
            "success": True,
            "message": f"已清除{memory_type or '全部'}记忆，共{deleted_count}条",
            "deleted_count": deleted_count,
        }
    
    def _save_memory(self, user_id: str, memory_type: str, key: str, value: str) -> None:
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO memories (user_id, memory_type, key, value, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(user_id, memory_type, key)
               DO UPDATE SET value = ?, updated_at = ?""",
            (user_id, memory_type, key, value, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"), value, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        
        conn.commit()
        conn.close()
        
        self._check_memory_limit(user_id)
    
    def _check_memory_limit(self, user_id: str) -> None:
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM memories WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        
        if count > self.config.memory_limit:
            excess = count - self.config.memory_limit
            cursor.execute(
                """DELETE FROM memories WHERE id IN (
                   SELECT id FROM memories WHERE user_id = ? ORDER BY created_at ASC LIMIT ?
                )""",
                (user_id, excess)
            )
            conn.commit()
            logger.info(f"记忆超限，已删除{excess}条旧记忆")
        
        conn.close()
    
    def learn_from_user_action(self, user_id: str, action_type: str, action_data: Dict[str, Any]) -> None:
        if action_type == "command_shortcut":
            self.record_command_shortcut(
                user_id,
                action_data.get("shortcut", ""),
                action_data.get("full_command", "")
            )
        
        elif action_type == "topic_assignment":
            self.record_topic_preference(
                user_id,
                action_data.get("content_pattern", ""),
                action_data.get("topic", "")
            )
        
        elif action_type == "output_preference":
            self.record_output_preference(
                user_id,
                action_data.get("preference_type", ""),
                action_data.get("value")
            )
