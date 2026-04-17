"""
哈希计算工具
"""

import hashlib
from typing import Union


def calculate_hash(content: Union[str, bytes], algorithm: str = "sha256") -> str:
    if isinstance(content, str):
        content = content.encode("utf-8")
    
    if algorithm == "md5":
        return hashlib.md5(content).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(content).hexdigest()
    elif algorithm == "sha512":
        return hashlib.sha512(content).hexdigest()
    else:
        raise ValueError(f"不支持的哈希算法: {algorithm}")


def calculate_text_hash(text: str, algorithm: str = "sha256") -> str:
    return calculate_hash(text, algorithm)
