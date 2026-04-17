"""
平台适配模块
包含微信、飞书、CLI等平台适配
"""

from .cli import CLIPlatform
from .wechat import WeChatPlatform
from .feishu import FeishuPlatform

__all__ = ["CLIPlatform", "WeChatPlatform", "FeishuPlatform"]
