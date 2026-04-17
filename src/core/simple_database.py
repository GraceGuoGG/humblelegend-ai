"""简单的内存数据库模块，无需SQLite依赖"""
import json
import os
from datetime import datetime, timedelta


class SimpleDatabase:
    """简单的内存数据库"""
    
    def __init__(self):
        self.data_file = "data/simple_data.json"
        self._data = self._load_data()
    
    def _load_data(self):
        """加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "users": [],
            "records": [],
            "calorie_records": [],
            "collections": [],
            "polish_records": [],
            "user_settings": {},
            "command_memory": []
        }
    
    def _save_data(self):
        """保存数据"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
    
    def get_or_create_user(self, user_id):
        """获取或创建用户"""
        if user_id not in [u["user_id"] for u in self._data["users"]]:
            self._data["users"].append({
                "user_id": user_id,
                "created_at": datetime.now().isoformat()
            })
            self._save_data()
    
    def add_record(self, user_id, content, theme):
        """添加记录"""
        self.get_or_create_user(user_id)
        self._data["records"].append({
            "id": len(self._data["records"]) + 1,
            "user_id": user_id,
            "content": content,
            "theme": theme,
            "created_at": datetime.now().isoformat()
        })
        self._save_data()
    
    def add_calorie_record(self, user_id, food, calorie):
        """添加卡路里记录"""
        self.get_or_create_user(user_id)
        self._data["calorie_records"].append({
            "id": len(self._data["calorie_records"]) + 1,
            "user_id": user_id,
            "food": food,
            "calorie": calorie,
            "created_at": datetime.now().isoformat()
        })
        self._save_data()
    
    def add_collection(self, user_id, title, content):
        """添加收藏记录"""
        self.get_or_create_user(user_id)
        self._data["collections"].append({
            "id": len(self._data["collections"]) + 1,
            "user_id": user_id,
            "title": title,
            "content": content,
            "created_at": datetime.now().isoformat()
        })
        self._save_data()
    
    def add_polish_record(self, user_id, original, polished, style):
        """添加润色记录"""
        self.get_or_create_user(user_id)
        self._data["polish_records"].append({
            "id": len(self._data["polish_records"]) + 1,
            "user_id": user_id,
            "original": original,
            "polished": polished,
            "style": style,
            "created_at": datetime.now().isoformat()
        })
        self._save_data()
    
    def add_command_memory(self, user_id, command_type, command_text):
        """添加命令记忆"""
        self.get_or_create_user(user_id)
        self._data["command_memory"].append({
            "id": len(self._data["command_memory"]) + 1,
            "user_id": user_id,
            "command_type": command_type,
            "command_text": command_text,
            "created_at": datetime.now().isoformat()
        })
        self._save_data()
    
    def get_records_by_date(self, user_id, query_date):
        """获取指定日期的记录"""
        date_str = query_date.strftime("%Y-%m-%d")
        records = [
            r for r in self._data["records"]
            if r["user_id"] == user_id and date_str in r["created_at"]
        ]
        return [self._to_row(record) for record in records]
    
    def get_calorie_records_by_date(self, user_id, query_date):
        """获取指定日期的卡路里记录"""
        date_str = query_date.strftime("%Y-%m-%d")
        records = [
            r for r in self._data["calorie_records"]
            if r["user_id"] == user_id and date_str in r["created_at"]
        ]
        return [self._to_row(record) for record in records]
    
    def get_collections_by_date(self, user_id, query_date):
        """获取指定日期的收藏记录"""
        date_str = query_date.strftime("%Y-%m-%d")
        records = [
            r for r in self._data["collections"]
            if r["user_id"] == user_id and date_str in r["created_at"]
        ]
        return [self._to_row(record) for record in records]
    
    def get_polish_records_by_date(self, user_id, query_date):
        """获取指定日期的润色记录"""
        date_str = query_date.strftime("%Y-%m-%d")
        records = [
            r for r in self._data["polish_records"]
            if r["user_id"] == user_id and date_str in r["created_at"]
        ]
        return [self._to_row(record) for record in records]
    
    def get_all_records(self, user_id, days=7):
        """获取指定天数内的所有记录"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        records = [
            r for r in self._data["records"]
            if r["user_id"] == user_id and
            start_date <= datetime.fromisoformat(r["created_at"]) <= end_date
        ]
        return [self._to_row(record) for record in records]
    
    def get_all_calorie_records(self, user_id, days=7):
        """获取指定天数内的所有卡路里记录"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        records = [
            r for r in self._data["calorie_records"]
            if r["user_id"] == user_id and
            start_date <= datetime.fromisoformat(r["created_at"]) <= end_date
        ]
        return [self._to_row(record) for record in records]
    
    def get_all_collections(self, user_id, days=7):
        """获取指定天数内的所有收藏记录"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        records = [
            r for r in self._data["collections"]
            if r["user_id"] == user_id and
            start_date <= datetime.fromisoformat(r["created_at"]) <= end_date
        ]
        return [self._to_row(record) for record in records]
    
    def get_all_polish_records(self, user_id, days=7):
        """获取指定天数内的所有润色记录"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        records = [
            r for r in self._data["polish_records"]
            if r["user_id"] == user_id and
            start_date <= datetime.fromisoformat(r["created_at"]) <= end_date
        ]
        return [self._to_row(record) for record in records]
    
    def get_records_by_theme(self, user_id, theme, days=7):
        """获取指定主题的记录"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        records = [
            r for r in self._data["records"]
            if r["user_id"] == user_id and
            r["theme"] == theme and
            start_date <= datetime.fromisoformat(r["created_at"]) <= end_date
        ]
        return [self._to_row(record) for record in records]
    
    def get_user_settings(self, user_id):
        """获取用户设置"""
        if user_id not in self._data["user_settings"]:
            self._data["user_settings"][user_id] = {
                "user_id": user_id,
                "daily_record_target": 5,
                "theme_settings": ["作息", "饮食", "工作", "娱乐"]
            }
            self._save_data()
        
        return self._to_row(self._data["user_settings"][user_id])
    
    def update_user_settings(self, user_id, theme_settings=None, daily_record_target=None):
        """更新用户设置"""
        settings = self.get_user_settings(user_id)
        if theme_settings:
            settings["theme_settings"] = theme_settings
        if daily_record_target is not None:
            settings["daily_record_target"] = daily_record_target
        self._data["user_settings"][user_id] = dict(settings)
        self._save_data()
    
    def _to_row(self, record):
        """转换为类似SQLite Row的对象"""
        class Row:
            def __init__(self, data):
                self._data = data
            
            def __getitem__(self, key):
                return self._data.get(key, None)
            
            def __getattr__(self, name):
                return self._data.get(name, None)
            
            def keys(self):
                return list(self._data.keys())
        
        return Row(record)