#!/usr/bin/env python3
"""项目部署准备检查脚本"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("=== 项目部署准备检查 ===")

try:
    from src.core.simple_app import SimpleHumbleLegendApp
    from src.platforms.feishu_mock import FeishuAdapter
    print("✅ 核心模块导入成功")
except Exception as e:
    print(f"❌ 核心模块导入失败: {e}")
    sys.exit(1)

try:
    app = SimpleHumbleLegendApp()
    print("✅ 应用初始化成功")
except Exception as e:
    print(f"❌ 应用初始化失败: {e}")
    sys.exit(1)

try:
    test_input = "帮我记录"
    result = app.process("test_user", test_input)
    print(f"✅ 命令处理成功: '{test_input}'")
    print(f"   结果: '{result}'")
except Exception as e:
    print(f"❌ 命令处理失败: {e}")
    import traceback
    print(traceback.format_exc())
    sys.exit(1)

try:
    feishu = FeishuAdapter({})
    print("✅ 飞书适配器初始化成功")
except Exception as e:
    print(f"❌ 飞书适配器初始化失败: {e}")
    sys.exit(1)

print("\n=== 项目部署准备检查完成 ===")
