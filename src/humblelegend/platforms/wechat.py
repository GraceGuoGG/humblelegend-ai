"""
微信平台适配
通过Webhook实现微信对话框交互
"""

from typing import Any, Dict, Optional
from loguru import logger

from ..agents.orchestrator import OrchestratorAgent
from ..core.config import Config


class WeChatPlatform:
    def __init__(self, config: Config):
        self.config = config
        self.orchestrator = OrchestratorAgent(config)
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        user_id = message.get("FromUserName", "default_user")
        content = message.get("Content", "")
        msg_type = message.get("MsgType", "text")
        
        attachments = []
        
        if msg_type == "image":
            pic_url = message.get("PicUrl")
            if pic_url:
                attachments.append({
                    "type": "image",
                    "url": pic_url,
                })
        
        elif msg_type == "video":
            video_url = message.get("VideoUrl") or message.get("MediaId")
            if video_url:
                attachments.append({
                    "type": "video",
                    "url": video_url,
                })
        
        elif msg_type == "link":
            url = message.get("Url")
            title = message.get("Title", "")
            description = message.get("Description", "")
            if url:
                content = f"{title}\n{description}\n{url}"
        
        response = self.orchestrator.process(content, user_id, attachments)
        
        return {
            "ToUserName": user_id,
            "FromUserName": message.get("ToUserName", ""),
            "CreateTime": message.get("CreateTime", 0),
            "MsgType": "text",
            "Content": response.message,
        }
    
    def get_menu_config(self) -> Dict[str, Any]:
        return {
            "button": [
                {
                    "type": "click",
                    "name": "记录日常",
                    "key": "record_daily"
                },
                {
                    "type": "click",
                    "name": "估算热量",
                    "key": "record_calorie"
                },
                {
                    "name": "更多",
                    "sub_button": [
                        {
                            "type": "click",
                            "name": "今日日报",
                            "key": "daily_report_today"
                        },
                        {
                            "type": "click",
                            "name": "内容收藏",
                            "key": "collect"
                        },
                        {
                            "type": "click",
                            "name": "文本润色",
                            "key": "polish"
                        }
                    ]
                }
            ]
        }
    
    def handle_menu_click(self, event_key: str, user_id: str) -> str:
        menu_to_command = {
            "record_daily": "帮我记录日常",
            "record_calorie": "帮我估算热量",
            "daily_report_today": "给我今日日报",
            "collect": "帮我收藏",
            "polish": "帮我润色",
        }
        
        command = menu_to_command.get(event_key, "")
        if not command:
            return "未知操作"
        
        response = self.orchestrator.process(command, user_id)
        return response.message
