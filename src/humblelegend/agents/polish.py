"""
文本润色Agent
根据用户需求润色文本，支持多种风格
"""

from typing import Any, Dict, Optional
from loguru import logger

from ..core.config import Config
from ..core.llm import get_llm_service


class PolishAgent:
    STYLE_PROMPTS = {
        "简洁化": "请将以下文本润色为简洁版本，去除冗余，保留核心信息：",
        "正式化": "请将以下文本润色为正式书面语，适合商务场景：",
        "生动化": "请将以下文本润色为更生动有趣的版本，增加修辞和感染力：",
        "默认": "请优化以下文本，使其更加通顺、清晰、易读：",
    }
    
    def __init__(self, config: Config):
        self.config = config
        self.llm = get_llm_service()
    
    def polish(self, text: str, style: str = "默认") -> Dict[str, Any]:
        if not text:
            return {
                "success": False,
                "message": "请提供要润色的文本内容",
            }
        
        style_prompt = self.STYLE_PROMPTS.get(style, self.STYLE_PROMPTS["默认"])
        
        prompt = f"""{style_prompt}

原文：
{text}

请直接返回润色后的文本，不要添加任何解释或说明。"""
        
        try:
            polished_text = self.llm.chat([{"role": "user", "content": prompt}])
            
            if not polished_text:
                return {
                    "success": False,
                    "message": "润色失败，请稍后重试",
                }
            
            return {
                "success": True,
                "original_text": text,
                "polished_text": polished_text.strip(),
                "style": style,
            }
            
        except Exception as e:
            logger.error(f"文本润色失败: {e}")
            return {
                "success": False,
                "message": f"润色失败: {str(e)}",
            }
    
    def polish_with_instructions(self, text: str, instructions: str) -> Dict[str, Any]:
        if not text:
            return {
                "success": False,
                "message": "请提供要润色的文本内容",
            }
        
        prompt = f"""请根据以下要求润色文本：

要求：{instructions}

原文：
{text}

请直接返回润色后的文本，不要添加任何解释或说明。"""
        
        try:
            polished_text = self.llm.chat([{"role": "user", "content": prompt}])
            
            if not polished_text:
                return {
                    "success": False,
                    "message": "润色失败，请稍后重试",
                }
            
            return {
                "success": True,
                "original_text": text,
                "polished_text": polished_text.strip(),
                "style": "自定义",
                "instructions": instructions,
            }
            
        except Exception as e:
            logger.error(f"文本润色失败: {e}")
            return {
                "success": False,
                "message": f"润色失败: {str(e)}",
            }
