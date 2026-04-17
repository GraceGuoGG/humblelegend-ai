"""设置Agent"""

import json
from sqlalchemy.orm import Session
from src.core.db_utils import DBUtils
from src.core.models import UserSetting


class SettingAgent:
    """设置Agent"""
    
    def __init__(self, db: Session):
        """初始化"""
        self.db = db
    
    def handle_setting(self, user_id: str, setting_type: str, value: str) -> str:
        """处理设置指令"""
        if setting_type == "主题":
            return self._handle_theme_setting(user_id, value)
        elif setting_type == "目标":
            return self._handle_target_setting(user_id, value)
        elif setting_type == "数据留存":
            return self._handle_retention_setting(user_id, value)
        elif setting_type == "查看设置":
            return self._handle_view_settings(user_id)
        else:
            return "抱歉，我没有理解您的设置指令。"
    
    def _handle_theme_setting(self, user_id: str, themes: str) -> str:
        """处理主题设置"""
        # 解析主题列表
        theme_list = [theme.strip() for theme in themes.split(",")]
        theme_json = json.dumps(theme_list, ensure_ascii=False)
        
        # 更新设置
        DBUtils.update_user_setting(self.db, user_id, theme_settings=theme_json)
        
        return f"已更新主题设置：{', '.join(theme_list)}"
    
    def _handle_target_setting(self, user_id: str, target_str: str) -> str:
        """处理目标设置"""
        # 解析目标设置
        targets = {}
        for item in target_str.split(","):
            item = item.strip()
            if "记录目标" in item:
                targets["daily_record_target"] = int(item.split("：")[1])
            elif "热量目标" in item:
                targets["daily_calorie_target"] = float(item.split("：")[1].replace("千卡", ""))
            elif "蛋白质目标" in item:
                targets["daily_protein_target"] = float(item.split("：")[1].replace("克", ""))
            elif "脂肪目标" in item:
                targets["daily_fat_target"] = float(item.split("：")[1].replace("克", ""))
            elif "碳水目标" in item:
                targets["daily_carbs_target"] = float(item.split("：")[1].replace("克", ""))
        
        # 更新设置
        if targets:
            DBUtils.update_user_setting(self.db, user_id, **targets)
            return f"已更新目标设置：{target_str}"
        else:
            return "抱歉，我没有理解您的目标设置指令。"
    
    def _handle_retention_setting(self, user_id: str, retention_str: str) -> str:
        """处理数据留存设置"""
        # 解析留存设置
        settings = {}
        for item in retention_str.split(","):
            item = item.strip()
            if "留存时间" in item:
                settings["data_retention_days"] = int(item.split("：")[1].replace("天", ""))
            elif "自动清理" in item:
                settings["auto_clean"] = "开启" in item
        
        # 更新设置
        if settings:
            DBUtils.update_user_setting(self.db, user_id, **settings)
            return f"已更新数据留存设置：{retention_str}"
        else:
            return "抱歉，我没有理解您的数据留存设置指令。"
    
    def _handle_view_settings(self, user_id: str) -> str:
        """查看设置"""
        setting = DBUtils.get_or_create_user_setting(self.db, user_id)
        
        # 解析主题设置
        theme_settings = json.loads(setting.theme_settings)
        
        # 构建设置信息
        settings_info = []
        settings_info.append("## 当前设置")
        settings_info.append(f"- **主题设置**：{', '.join(theme_settings)}")
        settings_info.append(f"- **每日记录目标**：{setting.daily_record_target} 条")
        settings_info.append(f"- **每日热量目标**：{setting.daily_calorie_target} 千卡")
        settings_info.append(f"- **每日蛋白质目标**：{setting.daily_protein_target} 克")
        settings_info.append(f"- **每日脂肪目标**：{setting.daily_fat_target} 克")
        settings_info.append(f"- **每日碳水目标**：{setting.daily_carbs_target} 克")
        settings_info.append(f"- **数据留存时间**：{setting.data_retention_days} 天")
        settings_info.append(f"- **自动清理**：{'开启' if setting.auto_clean else '关闭'}")
        
        return "\n".join(settings_info)
    
    def record_command(self, user_id: str, command_type: str, command_content: str) -> None:
        """记录指令记忆"""
        DBUtils.record_command_memory(self.db, user_id, command_type, command_content)
    
    def get_command_suggestions(self, user_id: str, limit: int = 5) -> list[str]:
        """获取指令建议"""
        memories = DBUtils.get_command_memories(self.db, user_id, limit)
        return [m.command_content for m in memories]