#!/usr/bin/env python3
import sys
import os

# 设置路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print('=== Python环境信息 ===')
print(f'版本: {sys.version}')
print(f'路径: {sys.executable}')
print()

try:
    print('=== 导入main.py ===')
    from main import main
    print('✅ main.py导入成功')
    print()
    
    print('=== 测试导入FastAPI ===')
    from src.api.server import start_server
    print('✅ FastAPI服务器导入成功')
    print()
    
    print('=== 测试配置 ===')
    from src.platforms.feishu_mock import FeishuAdapter
    feishu_config = {
        'app_id': 'cli_a955b0e8ad791bb4',
        'app_secret': 'Wvc7hHY2Gqe0Pks1wbXHCfFdjgPQlTXB',
        'verification_token': '',
        'encrypt_key': ''
    }
    
    adapter = FeishuAdapter(feishu_config)
    print('✅ 飞书适配器配置成功')
    
    token = adapter.get_access_token()
    print(f'✅ 获取到Token: {token}')
    print()
    
    print('=== 测试成功 ===')
    print('服务器可以正常启动')
    
except Exception as e:
    print(f'❌ 错误: {str(e)}')
    import traceback
    print(traceback.format_exc())
    sys.exit(1)
