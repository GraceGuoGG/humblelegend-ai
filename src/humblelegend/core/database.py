"""
数据库初始化脚本
创建所有必要的数据库表
"""

import sqlite3
from pathlib import Path
from loguru import logger


def init_database(db_path: str = "data/database.db") -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            settings TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            record_type TEXT NOT NULL,
            content TEXT NOT NULL,
            topics TEXT,
            metadata TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confirmed BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calorie_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id INTEGER NOT NULL,
            food_name TEXT NOT NULL,
            calories REAL NOT NULL,
            protein REAL,
            fat REAL,
            carbs REAL,
            sodium REAL,
            estimated_weight REAL,
            image_url TEXT,
            FOREIGN KEY (record_id) REFERENCES records(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id INTEGER NOT NULL,
            content_type TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            storage_path TEXT,
            url TEXT,
            FOREIGN KEY (record_id) REFERENCES records(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS polish_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id INTEGER NOT NULL,
            original_text TEXT NOT NULL,
            polished_text TEXT NOT NULL,
            style TEXT,
            FOREIGN KEY (record_id) REFERENCES records(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            report_date DATE NOT NULL,
            content TEXT NOT NULL,
            version INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            UNIQUE(user_id, report_date, version)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS review_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            memory_type TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            UNIQUE(user_id, memory_type, key)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            session_date DATE NOT NULL,
            command_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            UNIQUE(user_id, session_date)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_user_id ON records(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_timestamp ON records(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_type ON records(record_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_calorie_records_record_id ON calorie_records(record_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_collections_hash ON collections(content_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_reports_user_date ON daily_reports(user_id, report_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_user_type ON memories(user_id, memory_type)")
    
    conn.commit()
    conn.close()
    
    logger.info(f"数据库初始化完成: {db_path}")


if __name__ == "__main__":
    init_database()
