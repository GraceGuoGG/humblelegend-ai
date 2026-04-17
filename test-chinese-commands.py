#!/usr/bin/env python3
"""测试中文命令识别"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.simple_server import app_instance

test_texts = [
    '帮我记录完成了项目报告',
    '记录项目报告',
    '帮我记录',
    '完成了项目报告',
    '帮我记录完成了',
    '项目报告完成了'
]

print("=== HumbleLegend 中文命令识别测试 ===")
for text in test_texts:
    print()
    print(f"输入文本: \"{text}\"")
    
    try:
        command_type = app_instance._classify_command(text)
        result = app_instance.process('test_user', text)
        
        print(f"命令类型: {command_type}")
        print(f"输出结果: \"{result}\"")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        print(traceback.format_exc())
    
    print('-' * 60)

print()
print("=== 服务器内部应用类型 ===")
print(f"类型: {type(app_instance)}")