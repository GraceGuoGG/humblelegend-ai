"""数据库模型"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base


class RecordType(str, enum.Enum):
    """记录类型枚举"""
    DAILY = "日常记录"
    CALORIE = "热量记录"
    COLLECTION = "内容收藏"
    POLISH = "文本润色"


class ThemeType(str, enum.Enum):
    """主题类型枚举"""
    REST = "作息"
    DIET = "饮食"
    WORK = "工作"
    ENTERTAINMENT = "娱乐"


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    records = relationship("Record", back_populates="user")
    calorie_records = relationship("CalorieRecord", back_populates="user")
    collections = relationship("Collection", back_populates="user")
    polish_records = relationship("PolishRecord", back_populates="user")
    settings = relationship("UserSetting", back_populates="user", uselist=False)
    command_memories = relationship("CommandMemory", back_populates="user")


class Record(Base):
    """记录表"""
    __tablename__ = "records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    theme = Column(Enum(ThemeType), nullable=False)
    record_type = Column(Enum(RecordType), default=RecordType.DAILY)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="records")


class CalorieRecord(Base):
    """热量记录表"""
    __tablename__ = "calorie_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False)
    food = Column(String(200), nullable=False)
    calorie = Column(Float, nullable=False)
    protein = Column(Float, default=0.0)
    fat = Column(Float, default=0.0)
    carbs = Column(Float, default=0.0)
    sodium = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="calorie_records")


class Collection(Base):
    """收藏表"""
    __tablename__ = "collections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    url = Column(String(500))
    file_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="collections")


class PolishRecord(Base):
    """润色记录表"""
    __tablename__ = "polish_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False)
    original_text = Column(Text, nullable=False)
    polished_text = Column(Text, nullable=False)
    style = Column(String(100), default="default")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="polish_records")


class UserSetting(Base):
    """用户设置表"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), unique=True, nullable=False)
    daily_record_target = Column(Integer, default=5)
    daily_calorie_target = Column(Float, default=2000.0)
    daily_protein_target = Column(Float, default=70.0)
    daily_fat_target = Column(Float, default=65.0)
    daily_carbs_target = Column(Float, default=275.0)
    data_retention_days = Column(Integer, default=365)
    auto_clean = Column(Boolean, default=True)
    theme_settings = Column(Text, default='["作息", "饮食", "工作", "娱乐"]')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="settings")


class CommandMemory(Base):
    """指令记忆表"""
    __tablename__ = "command_memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False)
    command_type = Column(String(100), nullable=False)
    command_content = Column(Text, nullable=False)
    frequency = Column(Integer, default=1)
    last_used_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="command_memories")