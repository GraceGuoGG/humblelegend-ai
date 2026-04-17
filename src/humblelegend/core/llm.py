"""
LLM服务模块
封装火山引擎豆包模型API调用
"""

import os
from typing import Any, Dict, List, Optional
from loguru import logger

try:
    from volcengine.maas import MaasService, MaasException
    VOLCENGINE_AVAILABLE = True
except ImportError:
    VOLCENGINE_AVAILABLE = False
    logger.warning("volcengine未安装，LLM服务将使用模拟模式")


class LLMService:
    def __init__(
        self,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        model: str = "doubao-seed-1-6-vision-250815",
    ):
        self.access_key = access_key or os.getenv("VOLC_ACCESSKEY")
        self.secret_key = secret_key or os.getenv("VOLC_SECRETKEY")
        self.model = model
        self.maas = None
        
        if VOLCENGINE_AVAILABLE and self.access_key and self.secret_key:
            try:
                self.maas = MaasService(
                    "maas-api.ml-platform-cn-beijing.volces.com",
                    "cn-beijing"
                )
                self.maas.set_ak(self.access_key)
                self.maas.set_sk(self.secret_key)
                logger.info("火山引擎LLM服务初始化成功")
            except Exception as e:
                logger.error(f"火山引擎LLM服务初始化失败: {e}")
        else:
            logger.warning("LLM服务运行在模拟模式")
    
    def chat(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        if self.maas is None:
            return self._mock_chat(messages)
        
        try:
            req = {
                "model": model or self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            response = self.maas.chat(req)
            
            if response and "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"]
            else:
                logger.error(f"LLM响应格式异常: {response}")
                return ""
                
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            return self._mock_chat(messages)
    
    def chat_with_image(
        self,
        text: str,
        image_url: str,
        model: Optional[str] = None,
    ) -> str:
        if self.maas is None:
            return self._mock_vision_chat(text, image_url)
        
        try:
            req = {
                "model": model or self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": text},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ]
            }
            
            response = self.maas.chat(req)
            
            if response and "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"]
            else:
                logger.error(f"视觉LLM响应格式异常: {response}")
                return ""
                
        except Exception as e:
            logger.error(f"视觉LLM调用失败: {e}")
            return self._mock_vision_chat(text, image_url)
    
    def _mock_chat(self, messages: List[Dict[str, Any]]) -> str:
        last_message = messages[-1]["content"] if messages else ""
        logger.warning(f"模拟模式: 处理消息 '{last_message[:50]}...'")
        return f"[模拟响应] 已收到您的消息: {last_message[:100]}"
    
    def _mock_vision_chat(self, text: str, image_url: str) -> str:
        logger.warning(f"模拟模式: 处理图片 '{image_url[:50]}...'")
        return "[模拟响应] 已收到图片，识别结果: 米饭（约200克）"


llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    global llm_service
    if llm_service is None:
        from .config import load_config
        config = load_config()
        llm_service = LLMService(
            access_key=config.volc_access_key,
            secret_key=config.volc_secret_key,
            model=config.volc_model,
        )
    return llm_service
