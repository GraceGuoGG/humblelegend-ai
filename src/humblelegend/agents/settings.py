"""
设置Agent
处理所有设置类操作：主题、目标、数据留存
"""

import json
from typing import Any, Dict, List, Optional
from loguru import logger

from ..core.config import Config, save_soul_md, UserSettings, TopicConfig, NutritionGoal, SleepGoal, WaterGoal


class SettingsAgent:
    def __init__(self, config: Config):
        self.config = config
    
    def get_topics(self) -> List[Dict[str, str]]:
        return [{"name": t.name, "description": t.description} for t in self.config.user_settings.topics]
    
    def add_topic(self, name: str, description: str = "") -> Dict[str, Any]:
        for topic in self.config.user_settings.topics:
            if topic.name == name:
                return {
                    "success": False,
                    "message": f"主题「{name}」已存在",
                }
        
        self.config.user_settings.topics.append(TopicConfig(name=name, description=description))
        self._save_config()
        
        return {
            "success": True,
            "message": f"已新增主题：{name}",
            "topics": self.get_topics(),
        }
    
    def remove_topic(self, name: str) -> Dict[str, Any]:
        if len(self.config.user_settings.topics) <= 1:
            return {
                "success": False,
                "message": "至少需要保留一个主题",
            }
        
        for i, topic in enumerate(self.config.user_settings.topics):
            if topic.name == name:
                self.config.user_settings.topics.pop(i)
                self._save_config()
                return {
                    "success": True,
                    "message": f"已删除主题：{name}",
                    "topics": self.get_topics(),
                }
        
        return {
            "success": False,
            "message": f"主题「{name}」不存在",
        }
    
    def rename_topic(self, old_name: str, new_name: str) -> Dict[str, Any]:
        for topic in self.config.user_settings.topics:
            if topic.name == old_name:
                topic.name = new_name
                self._save_config()
                return {
                    "success": True,
                    "message": f"已将主题「{old_name}」重命名为「{new_name}」",
                    "topics": self.get_topics(),
                }
        
        return {
            "success": False,
            "message": f"主题「{old_name}」不存在",
        }
    
    def get_nutrition_goal(self) -> Dict[str, float]:
        return {
            "calories": self.config.user_settings.nutrition_goal.calories,
            "protein": self.config.user_settings.nutrition_goal.protein,
            "fat": self.config.user_settings.nutrition_goal.fat,
            "carbs": self.config.user_settings.nutrition_goal.carbs,
            "sodium": self.config.user_settings.nutrition_goal.sodium,
        }
    
    def set_nutrition_goal(self, **kwargs) -> Dict[str, Any]:
        if "calories" in kwargs:
            self.config.user_settings.nutrition_goal.calories = float(kwargs["calories"])
        if "protein" in kwargs:
            self.config.user_settings.nutrition_goal.protein = float(kwargs["protein"])
        if "fat" in kwargs:
            self.config.user_settings.nutrition_goal.fat = float(kwargs["fat"])
        if "carbs" in kwargs:
            self.config.user_settings.nutrition_goal.carbs = float(kwargs["carbs"])
        if "sodium" in kwargs:
            self.config.user_settings.nutrition_goal.sodium = float(kwargs["sodium"])
        
        self._save_config()
        
        return {
            "success": True,
            "message": "营养目标已更新",
            "nutrition_goal": self.get_nutrition_goal(),
        }
    
    def get_sleep_goal(self) -> Dict[str, str]:
        return {
            "wake_time": self.config.user_settings.sleep_goal.wake_time,
            "sleep_time": self.config.user_settings.sleep_goal.sleep_time,
        }
    
    def set_sleep_goal(self, wake_time: Optional[str] = None, sleep_time: Optional[str] = None) -> Dict[str, Any]:
        if wake_time:
            self.config.user_settings.sleep_goal.wake_time = wake_time
        if sleep_time:
            self.config.user_settings.sleep_goal.sleep_time = sleep_time
        
        self._save_config()
        
        return {
            "success": True,
            "message": "作息目标已更新",
            "sleep_goal": self.get_sleep_goal(),
        }
    
    def get_water_goal(self) -> Dict[str, int]:
        return {
            "daily_ml": self.config.user_settings.water_goal.daily_ml,
        }
    
    def set_water_goal(self, daily_ml: int) -> Dict[str, Any]:
        self.config.user_settings.water_goal.daily_ml = daily_ml
        self._save_config()
        
        return {
            "success": True,
            "message": "饮水目标已更新",
            "water_goal": self.get_water_goal(),
        }
    
    def get_all_settings(self) -> Dict[str, Any]:
        return {
            "topics": self.get_topics(),
            "nutrition_goal": self.get_nutrition_goal(),
            "sleep_goal": self.get_sleep_goal(),
            "water_goal": self.get_water_goal(),
            "data_retention_weeks": self.config.data_retention_weeks,
            "memory_limit": self.config.memory_limit,
        }
    
    def process_natural_language(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        
        if "主题" in text:
            if "新增" in text or "添加" in text:
                import re
                match = re.search(r"主题[：:]*\s*(.+?)(?:\s|$)", text)
                if match:
                    topic_name = match.group(1).strip()
                    return self.add_topic(topic_name)
            
            elif "删除" in text or "移除" in text:
                import re
                match = re.search(r"主题[：:]*\s*(.+?)(?:\s|$)", text)
                if match:
                    topic_name = match.group(1).strip()
                    return self.remove_topic(topic_name)
            
            elif "查询" in text or "查看" in text or "列表" in text:
                return {
                    "success": True,
                    "message": "当前主题列表",
                    "topics": self.get_topics(),
                }
        
        if "热量" in text or "卡路里" in text:
            import re
            match = re.search(r"(\d+)", text)
            if match:
                calories = int(match.group(1))
                return self.set_nutrition_goal(calories=calories)
        
        if "起床" in text:
            import re
            match = re.search(r"(\d{1,2}[:：]\d{2})", text)
            if match:
                wake_time = match.group(1).replace("：", ":")
                return self.set_sleep_goal(wake_time=wake_time)
        
        if "睡觉" in text:
            import re
            match = re.search(r"(\d{1,2}[:：]\d{2})", text)
            if match:
                sleep_time = match.group(1).replace("：", ":")
                return self.set_sleep_goal(sleep_time=sleep_time)
        
        if "饮水" in text or "喝水" in text:
            import re
            match = re.search(r"(\d+)", text)
            if match:
                daily_ml = int(match.group(1))
                return self.set_water_goal(daily_ml=daily_ml)
        
        return {
            "success": False,
            "message": "无法识别设置指令，请使用更明确的表述",
        }
    
    def _save_config(self) -> None:
        save_soul_md(self.config)
        logger.info("配置已保存到soul.md")
