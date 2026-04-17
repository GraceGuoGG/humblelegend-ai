"""数据库工具模块 - 简化版"""
import sqlite3
import os
import json
from datetime import datetime, date, time, timedelta

from .database import execute_query, DB_PATH, get_or_create_user


def _get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_records_by_date(user_id, query_date):
    """获取指定日期的记录"""
    date_str = query_date.strftime("%Y-%m-%d")
    query = '''
        SELECT * FROM records 
        WHERE user_id = ? AND created_at LIKE ?
    '''
    params = (user_id, f"{date_str}%")
    return execute_query(query, params)


def get_calorie_records_by_date(user_id, query_date):
    """获取指定日期的卡路里记录"""
    date_str = query_date.strftime("%Y-%m-%d")
    query = '''
        SELECT * FROM calorie_records 
        WHERE user_id = ? AND created_at LIKE ?
    '''
    params = (user_id, f"{date_str}%")
    return execute_query(query, params)


def get_collections_by_date(user_id, query_date):
    """获取指定日期的收藏记录"""
    date_str = query_date.strftime("%Y-%m-%d")
    query = '''
        SELECT * FROM collections 
        WHERE user_id = ? AND created_at LIKE ?
    '''
    params = (user_id, f"{date_str}%")
    return execute_query(query, params)


def get_polish_records_by_date(user_id, query_date):
    """获取指定日期的润色记录"""
    date_str = query_date.strftime("%Y-%m-%d")
    query = '''
        SELECT * FROM polish_records 
        WHERE user_id = ? AND created_at LIKE ?
    '''
    params = (user_id, f"{date_str}%")
    return execute_query(query, params)


def get_all_records(user_id, days=7):
    """获取指定天数内的所有记录"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
    
    query = '''
        SELECT * FROM records 
        WHERE user_id = ? AND created_at BETWEEN ? AND ?
    '''
    params = (user_id, start_date_str, end_date_str)
    return execute_query(query, params)


def get_all_calorie_records(user_id, days=7):
    """获取指定天数内的所有卡路里记录"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
    
    query = '''
        SELECT * FROM calorie_records 
        WHERE user_id = ? AND created_at BETWEEN ? AND ?
    '''
    params = (user_id, start_date_str, end_date_str)
    return execute_query(query, params)


def get_all_collections(user_id, days=7):
    """获取指定天数内的所有收藏记录"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
    
    query = '''
        SELECT * FROM collections 
        WHERE user_id = ? AND created_at BETWEEN ? AND ?
    '''
    params = (user_id, start_date_str, end_date_str)
    return execute_query(query, params)


def get_all_polish_records(user_id, days=7):
    """获取指定天数内的所有润色记录"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
    
    query = '''
        SELECT * FROM polish_records 
        WHERE user_id = ? AND created_at BETWEEN ? AND ?
    '''
    params = (user_id, start_date_str, end_date_str)
    return execute_query(query, params)


def get_records_by_theme(user_id, theme, days=7):
    """获取指定主题的记录"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
    
    query = '''
        SELECT * FROM records 
        WHERE user_id = ? AND theme = ? AND created_at BETWEEN ? AND ?
    '''
    params = (user_id, theme, start_date_str, end_date_str)
    return execute_query(query, params)


def add_record(user_id, content, theme):
    """添加记录"""
    query = '''
        INSERT INTO records (user_id, content, theme) VALUES (?, ?, ?)
    '''
    params = (user_id, content, theme)
    execute_query(query, params)


def add_calorie_record(user_id, food, calorie):
    """添加卡路里记录"""
    query = '''
        INSERT INTO calorie_records (user_id, food, calorie) VALUES (?, ?, ?)
    '''
    params = (user_id, food, calorie)
    execute_query(query, params)


def add_collection(user_id, title, content):
    """添加收藏记录"""
    query = '''
        INSERT INTO collections (user_id, title, content) VALUES (?, ?, ?)
    '''
    params = (user_id, title, content)
    execute_query(query, params)


def add_polish_record(user_id, original, polished, style):
    """添加润色记录"""
    query = '''
        INSERT INTO polish_records (user_id, original, polished, style) VALUES (?, ?, ?, ?)
    '''
    params = (user_id, original, polished, style)
    execute_query(query, params)


def get_user_settings(user_id):
    """获取用户设置"""
    query = '''
        SELECT * FROM user_settings WHERE user_id = ?
    '''
    params = (user_id,)
    results = execute_query(query, params)
    return results[0] if results else None


def update_user_settings(user_id, theme_settings=None, daily_record_target=None):
    """更新用户设置"""
    fields = []
    params = []
    
    if theme_settings:
        fields.append("theme_settings = ?")
        params.append(json.dumps(theme_settings))
    
    if daily_record_target is not None:
        fields.append("daily_record_target = ?")
        params.append(daily_record_target)
    
    params.append(user_id)
    
    query = f'''
        UPDATE user_settings SET {', '.join(fields)} WHERE user_id = ?
    '''
    execute_query(query, params)


def add_command_memory(user_id, command_type, command_text):
    """添加命令记忆"""
    query = '''
        INSERT INTO command_memory (user_id, command_type, command_text) VALUES (?, ?, ?)
    '''
    params = (user_id, command_type, command_text)
    execute_query(query, params)


def get_command_memory(user_id, days=7):
    """获取命令记忆"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
    
    query = '''
        SELECT * FROM command_memory 
        WHERE user_id = ? AND created_at BETWEEN ? AND ?
    '''
    params = (user_id, start_date_str, end_date_str)
    return execute_query(query, params)