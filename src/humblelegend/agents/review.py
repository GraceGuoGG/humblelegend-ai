"""
复盘Agent
生成主题复盘报告，展示趋势与分析
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from loguru import logger

from ..core.config import Config
from ..core.llm import get_llm_service
from ..utils.time import get_date


class ReviewAgent:
    def __init__(self, config: Config, db_path: str = "data/database.db"):
        self.config = config
        self.db_path = db_path
        self.llm = get_llm_service()
    
    def generate_review(self, user_id: str, topic: str) -> Dict[str, Any]:
        records = self._get_records_by_topic(user_id, topic)
        
        if not records:
            return {
                "success": False,
                "message": f"主题「{topic}」近8周内暂无记录",
            }
        
        trend_7d = self._calculate_trend(records, days=7)
        trend_8w = self._calculate_trend(records, days=56)
        
        summary = self._generate_summary(records, topic)
        
        topic_box = self._generate_topic_box(records)
        
        content = self._format_report(topic, trend_7d, trend_8w, summary, topic_box)
        
        self._save_review(user_id, topic, content)
        
        return {
            "success": True,
            "topic": topic,
            "content": content,
            "record_count": len(records),
        }
    
    def _get_records_by_topic(self, user_id: str, topic: str) -> List[Dict[str, Any]]:
        import sqlite3
        
        cutoff_date = (datetime.now() - timedelta(days=56)).strftime("%Y-%m-%d")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT id, record_type, content, topics, metadata, timestamp
               FROM records
               WHERE user_id = ? AND DATE(timestamp) >= ?
               ORDER BY timestamp""",
            (user_id, cutoff_date)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        records = []
        for row in rows:
            topics = json.loads(row[3]) if row[3] else []
            if topic in topics or topic == "全部":
                records.append({
                    "id": row[0],
                    "record_type": row[1],
                    "content": row[2],
                    "topics": topics,
                    "metadata": json.loads(row[4]) if row[4] else {},
                    "timestamp": row[5],
                })
        
        return records
    
    def _calculate_trend(self, records: List[Dict[str, Any]], days: int) -> Dict[str, Any]:
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        daily_counts = {}
        daily_calories = {}
        
        for record in records:
            date = record["timestamp"][:10]
            if date >= cutoff_date:
                daily_counts[date] = daily_counts.get(date, 0) + 1
                
                if record["record_type"] == "calorie" and record.get("metadata"):
                    daily_calories[date] = daily_calories.get(date, 0) + record["metadata"].get("calories", 0)
        
        dates = sorted(daily_counts.keys())
        counts = [daily_counts[d] for d in dates]
        calories = [daily_calories.get(d, 0) for d in dates]
        
        return {
            "dates": dates,
            "counts": counts,
            "calories": calories,
            "total_records": sum(counts),
            "avg_records": sum(counts) / len(counts) if counts else 0,
        }
    
    def _generate_summary(self, records: List[Dict[str, Any]], topic: str) -> str:
        records_text = "\n".join([
            f"- [{r['timestamp']}] {r['content'][:100]}"
            for r in records[:50]
        ])
        
        prompt = f"""请根据以下「{topic}」主题的记录，生成一份500-800字的复盘分析报告。

记录内容：
{records_text}

请分析：
1. 该主题的整体情况
2. 主要活动或事件
3. 发现的规律或问题
4. 改进建议（如有）

不要编造信息，严格基于提供的记录内容。"""
        
        try:
            summary = self.llm.chat([{"role": "user", "content": prompt}])
            return summary.strip()
        except Exception as e:
            logger.error(f"生成复盘总结失败: {e}")
            return f"该主题共有{len(records)}条记录。"
    
    def _generate_topic_box(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "timestamp": r["timestamp"],
                "type": r["record_type"],
                "content": r["content"],
            }
            for r in sorted(records, key=lambda x: x["timestamp"])
        ]
    
    def _format_report(
        self,
        topic: str,
        trend_7d: Dict[str, Any],
        trend_8w: Dict[str, Any],
        summary: str,
        topic_box: List[Dict[str, Any]],
    ) -> str:
        content = f"""# {topic}主题复盘报告

## 历史数据趋势

### 近7天趋势

```mermaid
xychart-beta
    title "近7天记录数量"
    x-axis [{', '.join([f'"{d[-5:]}"' for d in trend_7d['dates']])}]
    y-axis "记录数" 0 --> {max(trend_7d['counts']) + 2 if trend_7d['counts'] else 5}
    line [{', '.join(map(str, trend_7d['counts']))}]
```

### 近8周趋势

```mermaid
xychart-beta
    title "近8周记录数量"
    x-axis [{', '.join([f'"{d[-5:]}"' for d in trend_8w['dates'][-14:]])}]
    y-axis "记录数" 0 --> {max(trend_8w['counts'][-14:]) + 2 if trend_8w['counts'] else 5}
    line [{', '.join(map(str, trend_8w['counts'][-14:]))}]
```

## 主题总结

{summary}

## 主题Box

"""
        
        for item in topic_box:
            content += f"- [{item['timestamp']}] {item['content']}\n"
        
        return content
    
    def _save_review(self, user_id: str, topic: str, content: str) -> int:
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO review_reports (user_id, topic, content)
               VALUES (?, ?, ?)""",
            (user_id, topic, content)
        )
        
        review_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"复盘报告已保存: user={user_id}, topic={topic}")
        return review_id
