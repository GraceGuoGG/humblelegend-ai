"""数据库模块 - 简化版，只使用标准库"""
import sqlite3
import os
import json
from datetime import datetime, date, time

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "humblelegend.db")

def _get_db_connection():
    """获取数据库连接"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库"""
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            content TEXT,
            theme INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # 创建卡路里记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calorie_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            food TEXT,
            calorie REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # 创建收藏表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT,
            content TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # 创建润色记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS polish_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            original TEXT,
            polished TEXT,
            style TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # 创建用户设置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id TEXT PRIMARY KEY,
            daily_record_target INTEGER DEFAULT 5,
            theme_settings TEXT DEFAULT '["作息", "饮食", "工作", "娱乐"]',
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # 创建命令记忆表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS command_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            command_type TEXT,
            command_text TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_or_create_user(user_id):
    """获取或创建用户"""
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM users WHERE user_id = ?
    ''', (user_id,))
    
    user = cursor.fetchone()
    
    if not user:
        cursor.execute('''
            INSERT INTO users (user_id) VALUES (?)
        ''', (user_id,))
        
        # 同时创建用户设置
        cursor.execute('''
            INSERT INTO user_settings (user_id) VALUES (?)
        ''', (user_id,))
        
        conn.commit()
    
    conn.close()

def execute_query(query, params=()):
    """执行查询"""
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.fetchall()
    except Exception as e:
        print(f"数据库查询错误: {e}")
        conn.rollback()
        return []
    finally:
        conn.close()