#!/usr/bin/env python3
"""简化的启动测试"""

import sys
import os

print(f"Python版本: {sys.version}")
print(f"当前目录: {os.getcwd()}")
print(f"sys.path: {sys.path[:3]}")

try:
    from src.api.simple_server import start_server
    print("✅ 成功导入start_server")
    start_server('0.0.0.0', 8000)
except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback
    traceback.print_exc()
