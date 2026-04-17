"""
日报Agent
生成今日/历史日报，支持图表、修改、导出
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from loguru import logger

from ..core.config import Config
from ..core.llm import get_llm_service
from ..utils.time import get_date, parse_date, is_within_weeks


class DailyReportAgent:
    def __init__(self, config: Config, db_path: str = "data/database.db"):
        self.config = config
        self.db_path = db_path
        self.llm = get_llm_service()
    
    def generate_today_report(self, user_id: str = "default_user", with_chart: bool = False) -> Dict[str, Any]:
        today = get_date()
        return self.generate_report(user_id, today, with_chart)
    
    def generate_report(self, user_id: str, date: str, with_chart: bool = False) -> Dict[str, Any]:
        if not is_within_weeks(date, self.config.data_retention_weeks):
            return {
                "success": False,
                "message": f"仅支持最近{self.config.data_retention_weeks}周的日报查询",
            }
        
        records = self._get_records_by_date(user_id, date)
        
        if not records:
            return {
                "success": False,
                "message": "该日期暂无记录，请先添加记录后再生成日报",
            }
        
        stats = self._calculate_stats(user_id, date, records)
        
        summary = self._generate_summary(records, stats)
        
        topic_box = self._generate_topic_box(records)
        
        chart = None
        if with_chart:
            chart = self._generate_chart(stats)
        
        content = self._format_report(date, stats, summary, topic_box, chart)
        
        self._save_report(user_id, date, content)
        
        return {
            "success": True,
            "date": date,
            "content": content,
            "stats": stats,
            "with_chart": with_chart,
        }
    
    def _get_records_by_date(self, user_id: str, date: str) -> List[Dict[str, Any]]:
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT id, record_type, content, topics, metadata, timestamp, confirmed
               FROM records
               WHERE user_id = ? AND DATE(timestamp) = ?
               ORDER BY timestamp""",
            (user_id, date)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        records = []
        for row in rows:
            records.append({
                "id": row[0],
                "record_type": row[1],
                "content": row[2],
                "topics": json.loads(row[3]) if row[3] else [],
                "metadata": json.loads(row[4]) if row[4] else {},
                "timestamp": row[5],
                "confirmed": row[6],
            })
        
        return records
    
    def _calculate_stats(self, user_id: str, date: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT command_count FROM sessions WHERE user_id = ? AND session_date = ?",
            (user_id, date)
        )
        session_row = cursor.fetchone()
        session_count = session_row[0] if session_row else 0
        conn.close()
        
        record_count = len(records)
        daily_count = sum(1 for r in records if r["record_type"] == "daily")
        calorie_count = sum(1 for r in records if r["record_type"] == "calorie")
        collect_count = sum(1 for r in records if r["record_type"] == "collect")
        polish_count = sum(1 for r in records if r["record_type"] == "polish")
        
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        total_sodium = 0
        
        for record in records:
            if record["record_type"] == "calorie" and record.get("metadata"):
                meta = record["metadata"]
                total_calories += meta.get("calories", 0)
                total_protein += meta.get("protein", 0)
                total_fat += meta.get("fat", 0)
                total_carbs += meta.get("carbs", 0)
                total_sodium += meta.get("sodium", 0)
        
        topic_counts = {}
        for record in records:
            for topic in record.get("topics", []):
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        return {
            "session_count": session_count,
            "record_count": record_count,
            "daily_count": daily_count,
            "calorie_count": calorie_count,
            "collect_count": collect_count,
            "polish_count": polish_count,
            "total_calories": round(total_calories, 1),
            "total_protein": round(total_protein, 1),
            "total_fat": round(total_fat, 1),
            "total_carbs": round(total_carbs, 1),
            "total_sodium": round(total_sodium, 1),
            "topic_counts": topic_counts,
        }
    
    def _generate_summary(self, records: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
        records_text = "\n".join([
            f"- [{r['timestamp']}] {r['record_type']}: {r['content'][:100]}"
            for r in records
        ])
        
        prompt = f"""请根据以下用户今日记录，生成一份500-800字的日报总结。

今日记录：
{records_text}

统计数据：
- 记录总数：{stats['record_count']}
- 日常记录：{stats['daily_count']}条
- 热量估算：{stats['calorie_count']}次
- 收藏：{stats['collect_count']}条
- 润色：{stats['polish_count']}条

请总结用户今日的核心事件、活动、饮食情况等，不要编造信息，严格基于提供的记录内容。"""
        
        try:
            summary = self.llm.chat([{"role": "user", "content": prompt}])
            return summary.strip()
        except Exception as e:
            logger.error(f"生成日报总结失败: {e}")
            return f"今日共完成{stats['record_count']}条记录。"
    
    def _generate_topic_box(self, records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        topic_box = {}
        
        for record in records:
            topics = record.get("topics", [])
            if not topics:
                topics = ["未分类"]
            
            for topic in topics:
                if topic not in topic_box:
                    topic_box[topic] = []
                
                topic_box[topic].append({
                    "timestamp": record["timestamp"],
                    "type": record["record_type"],
                    "content": record["content"],
                })
        
        for topic in topic_box:
            topic_box[topic].sort(key=lambda x: x["timestamp"])
        
        return topic_box
    
    def _generate_chart(self, stats: Dict[str, Any]) -> str:
        chart = f"""```mermaid
%%{{init: {{'theme': 'base', 'themeVariables': {{'primaryColor': '#ffcc00'}}}}}}%%
pie title 今日记录分布
    "日常记录" : {stats['daily_count']}
    "热量估算" : {stats['calorie_count']}
    "内容收藏" : {stats['collect_count']}
    "文本润色" : {stats['polish_count']}
```"""
        return chart
    
    def _format_report(
        self,
        date: str,
        stats: Dict[str, Any],
        summary: str,
        topic_box: Dict[str, List[Dict[str, Any]]],
        chart: Optional[str],
    ) -> str:
        content = f"""# {date} 日报

## 数据卡片

| 指标 | 数值 |
|------|------|
| 今日消息会话数 | {stats['session_count']} |
| 今日记录总数 | {stats['record_count']} |
| 日常记录 | {stats['daily_count']} |
| 热量估算 | {stats['calorie_count']} |
| 内容收藏 | {stats['collect_count']} |
| 文本润色 | {stats['polish_count']} |
"""
        
        if stats['calorie_count'] > 0:
            content += f"""
### 营养摄入汇总

| 营养素 | 摄入量 |
|--------|--------|
| 热量 | {stats['total_calories']} 千卡 |
| 蛋白质 | {stats['total_protein']} 克 |
| 脂肪 | {stats['total_fat']} 克 |
| 碳水化合物 | {stats['total_carbs']} 克 |
| 钠 | {stats['total_sodium']} 毫克 |
"""
        
        if chart:
            content += f"\n### 图表\n\n{chart}\n"
        
        content += f"""
## 当日总结

{summary}

## 主题Box
"""
        
        for topic, items in topic_box.items():
            content += f"\n### {topic}\n\n"
            for item in items:
                content += f"- [{item['timestamp']}] {item['content']}\n"
        
        return content
    
    def _save_report(self, user_id: str, date: str, content: str) -> int:
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT MAX(version) FROM daily_reports WHERE user_id = ? AND report_date = ?""",
            (user_id, date)
        )
        max_version = cursor.fetchone()[0] or 0
        
        cursor.execute(
            """INSERT INTO daily_reports (user_id, report_date, content, version)
               VALUES (?, ?, ?, ?)""",
            (user_id, date, content, max_version + 1)
        )
        
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"日报已保存: user={user_id}, date={date}, version={max_version + 1}")
        return report_id
    
    def get_report_versions(self, user_id: str, date: str) -> List[Dict[str, Any]]:
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT id, content, version, created_at 
               FROM daily_reports 
               WHERE user_id = ? AND report_date = ?
               ORDER BY version""",
            (user_id, date)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "content": row[1],
                "version": row[2],
                "created_at": row[3],
            }
            for row in rows
        ]
