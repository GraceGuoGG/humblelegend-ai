import urllib.request
import json

try:
    req = urllib.request.Request('http://localhost:8000/health')
    with urllib.request.urlopen(req, timeout=3) as response:
        result = response.read().decode('utf-8')
        print('服务器状态:', json.loads(result))
except Exception as e:
    print('服务器未运行:', e)
