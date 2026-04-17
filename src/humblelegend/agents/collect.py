"""
内容收藏Agent
收藏各类内容（文本、图片、视频、链接），支持去重
"""

from typing import Any, Dict, List, Optional
from loguru import logger

from ..core.config import Config
from ..core.storage import get_storage_service
from ..utils.hash import calculate_hash, calculate_text_hash


class CollectAgent:
    def __init__(self, config: Config):
        self.config = config
        self.storage = get_storage_service()
    
    def collect(
        self,
        content: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
        user_id: str = "default_user",
    ) -> Dict[str, Any]:
        if not content and not attachments:
            return {
                "success": False,
                "message": "请提供要收藏的内容",
            }
        
        content_type = self._detect_content_type(content, attachments)
        
        content_hash = self._calculate_content_hash(content, attachments)
        
        if self._check_duplicate(content_hash, user_id):
            return {
                "success": False,
                "message": "该内容已收藏过",
                "is_duplicate": True,
                "content_hash": content_hash,
            }
        
        storage_path = None
        url = None
        
        if content_type == "image" and attachments:
            image = attachments[0]
            if "data" in image:
                storage_path = self.storage.save_file(
                    user_id=user_id,
                    file_content=image["data"],
                    file_extension=".jpg",
                )
            url = image.get("url")
        
        elif content_type == "link":
            url = self._extract_url(content)
        
        return {
            "success": True,
            "content": content,
            "content_type": content_type,
            "content_hash": content_hash,
            "storage_path": storage_path,
            "url": url,
        }
    
    def _detect_content_type(self, content: str, attachments: Optional[List[Dict[str, Any]]]) -> str:
        if attachments:
            for attachment in attachments:
                if attachment.get("type") == "image":
                    return "image"
                elif attachment.get("type") == "video":
                    return "video"
        
        if self._is_url(content):
            return "link"
        
        return "text"
    
    def _is_url(self, content: str) -> bool:
        import re
        url_pattern = r'https?://[^\s]+'
        return bool(re.search(url_pattern, content))
    
    def _extract_url(self, content: str) -> Optional[str]:
        import re
        url_pattern = r'(https?://[^\s]+)'
        match = re.search(url_pattern, content)
        return match.group(1) if match else None
    
    def _calculate_content_hash(self, content: str, attachments: Optional[List[Dict[str, Any]]]) -> str:
        if attachments:
            for attachment in attachments:
                if "data" in attachment:
                    return calculate_hash(attachment["data"])
                elif "url" in attachment:
                    return calculate_text_hash(attachment["url"])
        
        return calculate_text_hash(content)
    
    def _check_duplicate(self, content_hash: str, user_id: str) -> bool:
        import sqlite3
        
        conn = sqlite3.connect(self.config.database_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT COUNT(*) FROM collections c
               JOIN records r ON c.record_id = r.id
               WHERE c.content_hash = ? AND r.user_id = ?""",
            (content_hash, user_id)
        )
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
