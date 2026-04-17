#!/usr/bin/env python3
from src.platforms.feishu_fixed import FeishuAdapter
import urllib.request
import json

print("HumbleLegend 系统测试")
print("=" * 50)

# 测试健康检查
try:
    req = urllib.request.Request('http://localhost:8000/health')
    with urllib.request.urlopen(req, timeout=3) as response:
        result = response.read().decode('utf-8')
        print("1. 健康检查通过: {}".format(json.loads(result)))
except Exception as e:
    print("1. 健康检查失败: {}".format(e))

# 测试应用功能
try:
    adapter = FeishuAdapter({
        'app_id': 'cli_a955b0e8ad791bb4',
        'app_secret': 'Wvc7hHY2Gqe0Pks1wbXHCfFdjgPQlTXB'
    })
    
    # 测试命令
    print("\n2. 测试命令处理:")
    result = adapter.handle_command("test_user", "帮我记录完成了项目报告")
    print(result[:200] + "..." if len(result) > 200 else result)
    
except Exception as e:
    print("\n2. 命令处理失败: {}".format(e))
    import traceback
    print(traceback.format_exc())