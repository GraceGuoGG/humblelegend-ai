#!/usr/bin/env python3
"""直接运行服务器的简单测试脚本"""

import sys
import os
import subprocess

# 确保我们在正确的目录中
os.chdir(os.path.abspath(os.path.dirname(__file__)))

print("=== 测试服务器启动 ===\n")
print(f"当前工作目录: {os.getcwd()}")
print(f"Python路径: {sys.executable}")

try:
    # 运行服务器
    result = subprocess.run(
        [
            sys.executable, 
            "main.py", 
            "--mode", "api"
        ],
        cwd=os.getcwd(),
        capture_output=True,
        text=True,
        timeout=10
    )
    
    print("========================")
    print("标准输出 (stdout):")
    print("------------------------")
    print(result.stdout)
    print("\n========================")
    print("错误输出 (stderr):")
    print("------------------------")
    print(result.stderr)
    print("\n========================")
    print(f"返回码 (returncode): {result.returncode}")
    
except subprocess.TimeoutExpired:
    print("\n❌ 服务器启动超时")
except Exception as e:
    print(f"\n❌ 执行命令失败: {str(e)}")
    import traceback
    print(traceback.format_exc())
