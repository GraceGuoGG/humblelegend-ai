"""
存储服务模块
处理文件上传、存储、导出等操作
"""

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from loguru import logger


class StorageService:
    def __init__(self, storage_path: str = "data/uploads"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def save_file(
        self,
        user_id: str,
        file_content: bytes,
        file_extension: str = "",
        date: Optional[str] = None,
    ) -> str:
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{user_id}_{date}_{timestamp}{file_extension}"
        
        user_dir = self.storage_path / user_id / date
        user_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = user_dir / filename
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"文件已保存: {file_path}")
        return str(file_path)
    
    def save_json(
        self,
        user_id: str,
        data: Dict[str, Any],
        filename: str,
        date: Optional[str] = None,
    ) -> str:
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        user_dir = self.storage_path / user_id / date
        user_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = user_dir / f"{filename}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON已保存: {file_path}")
        return str(file_path)
    
    def save_markdown(
        self,
        user_id: str,
        content: str,
        filename: str,
        date: Optional[str] = None,
    ) -> str:
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        user_dir = self.storage_path / user_id / date
        user_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = user_dir / f"{filename}.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"Markdown已保存: {file_path}")
        return str(file_path)
    
    def calculate_hash(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()
    
    def calculate_text_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    
    def file_exists(self, file_path: str) -> bool:
        return Path(file_path).exists()
    
    def delete_file(self, file_path: str) -> bool:
        try:
            Path(file_path).unlink()
            logger.info(f"文件已删除: {file_path}")
            return True
        except Exception as e:
            logger.error(f"文件删除失败: {e}")
            return False
    
    def get_user_storage_size(self, user_id: str) -> int:
        user_dir = self.storage_path / user_id
        if not user_dir.exists():
            return 0
        
        total_size = 0
        for file in user_dir.rglob("*"):
            if file.is_file():
                total_size += file.stat().st_size
        return total_size
    
    def cleanup_old_files(self, user_id: str, retention_days: int = 56) -> int:
        user_dir = self.storage_path / user_id
        if not user_dir.exists():
            return 0
        
        cutoff_date = datetime.now().timestamp() - (retention_days * 24 * 60 * 60)
        deleted_count = 0
        
        for file in user_dir.rglob("*"):
            if file.is_file() and file.stat().st_mtime < cutoff_date:
                file.unlink()
                deleted_count += 1
        
        logger.info(f"清理旧文件: 用户 {user_id}, 删除 {deleted_count} 个文件")
        return deleted_count


storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    global storage_service
    if storage_service is None:
        from .config import load_config
        config = load_config()
        storage_service = StorageService(storage_path=config.storage_path)
    return storage_service
