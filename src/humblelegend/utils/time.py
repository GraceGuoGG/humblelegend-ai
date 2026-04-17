"""
时间处理工具
"""

from datetime import datetime, timezone, timedelta
from typing import Optional


def get_timestamp(timezone_offset: int = 8) -> str:
    tz = timezone(timedelta(hours=timezone_offset))
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")


def format_timestamp(timestamp: Optional[str] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    if timestamp is None:
        return datetime.now().strftime(fmt)
    
    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        return dt.strftime(fmt)
    except ValueError:
        return timestamp


def get_date(timezone_offset: int = 8) -> str:
    tz = timezone(timedelta(hours=timezone_offset))
    return datetime.now(tz).strftime("%Y-%m-%d")


def parse_date(date_str: str) -> Optional[datetime]:
    formats = ["%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def is_within_weeks(date_str: str, weeks: int = 8) -> bool:
    try:
        date = parse_date(date_str)
        if date is None:
            return False
        
        now = datetime.now()
        delta = now - date
        return delta.days <= weeks * 7
    except Exception:
        return False
