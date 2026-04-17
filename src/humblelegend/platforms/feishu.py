"""
飞书平台适配
通过Webhook实现飞书对话框交互
"""

from typing import Any, Dict, Optional
from loguru import logger

from ..agents.orchestrator import OrchestratorAgent
from ..core.config import Config


class FeishuPlatform:
    def __init__(self, config: Config):
        self.config = config
        self.orchestrator = OrchestratorAgent(config)
    
    def handle_message(self, event: Dict[str, Any]) -> Dict[str, Any]:
        message = event.get("message", {})
        content = message.get("content", "")
        msg_type = message.get("msg_type", "text")
        user_id = message.get("sender", {}).get("sender_id", {}).get("user_id", "default_user")
        
        attachments = []
        
        if msg_type == "image":
            image_key = message.get("content", {}).get("image_key")
            if image_key:
                attachments.append({
                    "type": "image",
                    "key": image_key,
                })
        
        elif msg_type == "file":
            file_key = message.get("content", {}).get("file_key")
            file_name = message.get("content", {}).get("file_name", "")
            if file_key:
                attachments.append({
                    "type": "file",
                    "key": file_key,
                    "name": file_name,
                })
        
        response = self.orchestrator.process(content, user_id, attachments)
        
        return {
            "msg_type": "text",
            "content": {
                "text": response.message
            }
        }
    
    def get_card_config(self) -> Dict[str, Any]:
        return {
            "type": "template",
            "data": {
                "template_id": "quick_actions",
                "template_variable": {
                    "actions": [
                        {"text": "记录日常", "value": "record_daily"},
                        {"text": "估算热量", "value": "record_calorie"},
                        {"text": "今日日报", "value": "daily_report_today"},
                        {"text": "内容收藏", "value": "collect"},
                        {"text": "文本润色", "value": "polish"},
                    ]
                }
            }
        }
    
    def handle_card_action(self, action_value: str, user_id: str) -> Dict[str, Any]:
        action_to_command = {
            "record_daily": "帮我记录日常",
            "record_calorie": "帮我估算热量",
            "daily_report_today": "给我今日日报",
            "collect": "帮我收藏",
            "polish": "帮我润色",
        }
        
        command = action_to_command.get(action_value, "")
        if not command:
            return {
                "msg_type": "text",
                "content": {"text": "未知操作"}
            }
        
        response = self.orchestrator.process(command, user_id)
        
        return {
            "msg_type": "text",
            "content": {"text": response.message}
        }
