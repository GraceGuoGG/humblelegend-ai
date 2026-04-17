"""
配置管理模块
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from loguru import logger


class TopicConfig(BaseModel):
    name: str
    description: str = ""


class NutritionGoal(BaseModel):
    calories: float = Field(default=2000, description="每日热量目标(千卡)")
    protein: float = Field(default=60, description="每日蛋白质目标(克)")
    fat: float = Field(default=65, description="每日脂肪目标(克)")
    carbs: float = Field(default=300, description="每日碳水化合物目标(克)")
    sodium: float = Field(default=2000, description="每日钠目标(毫克)")


class SleepGoal(BaseModel):
    wake_time: str = Field(default="07:00", description="起床时间")
    sleep_time: str = Field(default="23:00", description="睡觉时间")


class WaterGoal(BaseModel):
    daily_ml: int = Field(default=2000, description="每日饮水量(毫升)")


class UserSettings(BaseModel):
    topics: List[TopicConfig] = Field(
        default_factory=lambda: [
            TopicConfig(name="饮食作息", description="饮食、睡眠、运动相关记录"),
            TopicConfig(name="工作", description="工作任务、会议、项目相关记录"),
            TopicConfig(name="娱乐", description="娱乐、休闲、爱好相关记录"),
        ]
    )
    nutrition_goal: NutritionGoal = Field(default_factory=NutritionGoal)
    sleep_goal: SleepGoal = Field(default_factory=SleepGoal)
    water_goal: WaterGoal = Field(default_factory=WaterGoal)
    custom_goals: Dict[str, Any] = Field(default_factory=dict)


class Config(BaseModel):
    user_id: str = Field(default="default_user", description="用户ID")
    timezone: str = Field(default="Asia/Shanghai", description="时区")
    language: str = Field(default="zh", description="语言")
    data_retention_weeks: int = Field(default=8, description="数据保留周数")
    memory_limit: int = Field(default=3000, description="记忆容量上限")
    confirmation_timeout_minutes: int = Field(default=5, description="确认超时时间(分钟)")
    user_settings: UserSettings = Field(default_factory=UserSettings)
    
    volc_access_key: Optional[str] = Field(default=None, description="火山引擎AccessKey")
    volc_secret_key: Optional[str] = Field(default=None, description="火山引擎SecretKey")
    volc_model: str = Field(default="doubao-seed-1-6-vision-250815", description="火山引擎模型ID")
    
    database_path: str = Field(default="data/database.db", description="数据库路径")
    storage_path: str = Field(default="data/uploads", description="文件存储路径")
    log_path: str = Field(default="logs", description="日志路径")
    log_level: str = Field(default="INFO", description="日志级别")


def load_config(config_path: Optional[str] = None) -> Config:
    load_dotenv()
    
    config = Config()
    
    volc_ak = os.getenv("VOLC_ACCESSKEY")
    if volc_ak:
        config.volc_access_key = volc_ak
    volc_sk = os.getenv("VOLC_SECRETKEY")
    if volc_sk:
        config.volc_secret_key = volc_sk
    
    if config_path and Path(config_path).exists():
        logger.info(f"加载配置文件: {config_path}")
    
    return config


def save_soul_md(config: Config, soul_md_path: str = "config/soul.md") -> None:
    Path(soul_md_path).parent.mkdir(parents=True, exist_ok=True)
    
    content = f"""# HumbleLegend 用户配置文件

## 基本信息
- 用户ID: {config.user_id}
- 时区: {config.timezone}
- 语言: {config.language}

## 主题设置
"""
    for topic in config.user_settings.topics:
        content += f"- {topic.name}"
        if topic.description:
            content += f": {topic.description}"
        content += "\n"
    
    content += f"""
## 目标设置

### 营养目标
- 每日热量: {config.user_settings.nutrition_goal.calories} 千卡
- 每日蛋白质: {config.user_settings.nutrition_goal.protein} 克
- 每日脂肪: {config.user_settings.nutrition_goal.fat} 克
- 每日碳水化合物: {config.user_settings.nutrition_goal.carbs} 克
- 每日钠: {config.user_settings.nutrition_goal.sodium} 毫克

### 作息目标
- 起床时间: {config.user_settings.sleep_goal.wake_time}
- 睡觉时间: {config.user_settings.sleep_goal.sleep_time}

### 饮水目标
- 每日饮水量: {config.user_settings.water_goal.daily_ml} 毫升

## 数据设置
- 数据保留周数: {config.data_retention_weeks}
- 记忆容量上限: {config.memory_limit}
- 确认超时时间: {config.confirmation_timeout_minutes} 分钟
"""
    
    with open(soul_md_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    logger.info(f"配置已保存: {soul_md_path}")
