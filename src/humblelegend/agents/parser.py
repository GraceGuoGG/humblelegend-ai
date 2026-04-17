"""
指令解析Agent
解析用户输入，识别指令类型、参数、内容
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from loguru import logger


class IntentType(Enum):
    RECORD_DAILY = "record_daily"
    RECORD_CALORIE = "record_calorie"
    COLLECT = "collect"
    POLISH = "polish"
    DAILY_REPORT_TODAY = "daily_report_today"
    DAILY_REPORT_HISTORY = "daily_report_history"
    REVIEW = "review"
    SETTINGS = "settings"
    MEMORY_CLEAR = "memory_clear"
    MEMORY_QUERY = "memory_query"
    UNKNOWN = "unknown"


@dataclass
class ParsedCommand:
    intent: IntentType
    content: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    raw_input: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent.value,
            "content": self.content,
            "params": self.params,
            "attachments": self.attachments,
            "raw_input": self.raw_input,
            "timestamp": self.timestamp,
        }


class ParserAgent:
    COMMAND_PATTERNS = {
        IntentType.RECORD_DAILY: [
            r"帮我记录日常",
            r"记录日常",
            r"记日常",
            r"帮我记一下",
            r"记录一下",
        ],
        IntentType.RECORD_CALORIE: [
            r"帮我估算热量",
            r"估算热量",
            r"算热量",
            r"帮我算一下热量",
            r"记录饮食",
            r"记饮食",
        ],
        IntentType.COLLECT: [
            r"帮我收藏",
            r"收藏",
            r"收藏一下",
            r"帮我存一下",
        ],
        IntentType.POLISH: [
            r"帮我润色",
            r"润色",
            r"润色一下",
            r"帮我改一下",
            r"优化一下这段话",
        ],
        IntentType.DAILY_REPORT_TODAY: [
            r"给我今日日报",
            r"今日日报",
            r"今天的日报",
            r"给我今天的日报",
        ],
        IntentType.DAILY_REPORT_HISTORY: [
            r"给我(\d{4}[-年]\d{1,2}[-月]\d{1,2})日报",
            r"(\d{4}[-年]\d{1,2}[-月]\d{1,2})的日报",
        ],
        IntentType.REVIEW: [
            r"给我(.+?)主题复盘",
            r"(.+?)主题复盘",
            r"复盘(.+?)主题",
        ],
        IntentType.SETTINGS: [
            r"设置主题",
            r"新增主题",
            r"修改主题",
            r"设置目标",
            r"修改目标",
            r"设置热量目标",
            r"设置作息目标",
        ],
        IntentType.MEMORY_CLEAR: [
            r"清除我的指令记忆",
            r"清除记忆",
            r"删除记忆",
            r"清空记忆",
        ],
        IntentType.MEMORY_QUERY: [
            r"查询我的记忆",
            r"我的记忆",
            r"查看记忆",
        ],
    }
    
    def __init__(self):
        self.memory_agent = None
    
    def set_memory_agent(self, memory_agent):
        self.memory_agent = memory_agent
    
    def parse(self, user_input: str, attachments: Optional[List[Dict[str, Any]]] = None) -> ParsedCommand:
        raw_input = user_input
        user_input = user_input.strip()
        
        if self.memory_agent:
            user_input = self.memory_agent.apply_command_shortcuts(user_input)
        
        intent = self._detect_intent(user_input)
        content = self._extract_content(user_input, intent)
        params = self._extract_params(user_input, intent)
        
        command = ParsedCommand(
            intent=intent,
            content=content,
            params=params,
            attachments=attachments or [],
            raw_input=raw_input,
        )
        
        logger.info(f"指令解析完成: intent={intent.value}, content={content[:50]}...")
        return command
    
    def _detect_intent(self, user_input: str) -> IntentType:
        for intent, patterns in self.COMMAND_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, user_input):
                    return intent
        return IntentType.UNKNOWN
    
    def _extract_content(self, user_input: str, intent: IntentType) -> str:
        content = user_input
        
        for patterns in self.COMMAND_PATTERNS.values():
            for pattern in patterns:
                content = re.sub(pattern, "", content, count=1)
        
        content = content.strip()
        
        if intent == IntentType.DAILY_REPORT_HISTORY:
            date_match = re.search(r"(\d{4}[-年]\d{1,2}[-月]\d{1,2})", user_input)
            if date_match:
                return date_match.group(1).replace("年", "-").replace("月", "-").rstrip("日")
        
        if intent == IntentType.REVIEW:
            topic_match = re.search(r"(.+?)主题复盘|复盘(.+?)主题", user_input)
            if topic_match:
                return topic_match.group(1) or topic_match.group(2)
        
        return content
    
    def _extract_params(self, user_input: str, intent: IntentType) -> Dict[str, Any]:
        params = {}
        
        if intent == IntentType.DAILY_REPORT_TODAY:
            if "带图表" in user_input or "有图表" in user_input:
                params["with_chart"] = True
            else:
                params["with_chart"] = False
        
        if intent == IntentType.DAILY_REPORT_HISTORY:
            date_match = re.search(r"(\d{4}[-年]\d{1,2}[-月]\d{1,2})", user_input)
            if date_match:
                date_str = date_match.group(1).replace("年", "-").replace("月", "-").rstrip("日")
                params["date"] = date_str
        
        if intent == IntentType.POLISH:
            if "简洁" in user_input:
                params["style"] = "简洁化"
            elif "正式" in user_input:
                params["style"] = "正式化"
            elif "生动" in user_input:
                params["style"] = "生动化"
            else:
                params["style"] = "默认"
        
        if intent == IntentType.SETTINGS:
            if "主题" in user_input:
                params["setting_type"] = "topic"
            elif "热量" in user_input or "卡路里" in user_input:
                params["setting_type"] = "nutrition"
            elif "作息" in user_input:
                params["setting_type"] = "sleep"
            elif "饮水" in user_input:
                params["setting_type"] = "water"
        
        return params
    
    def get_command_suggestions(self) -> List[str]:
        return [
            "帮我记录日常 + 内容",
            "帮我估算热量 + 食物描述/图片",
            "帮我收藏 + 内容/链接",
            "帮我润色 + 文本内容",
            "给我今日日报",
            "给我YYYY-MM-DD日报",
            "给我XX主题复盘",
            "设置主题/目标",
        ]
