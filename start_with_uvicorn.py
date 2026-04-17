#!/usr/bin/env python3
"""
使用uvicorn直接启动服务器的Python脚本
"""

import sys
import os
import subprocess
import time
import urllib.request
import json

# 设置项目路径
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

def main():
    print('=== HumbleLegend 服务器启动 ===')
    print(f'Python版本: {sys.version}')
    print(f'项目路径: {PROJECT_ROOT}')
    print()

    try:
        # 检查是否已安装uvicorn
        print('检查依赖...')
        try:
            import uvicorn
            print('✅ uvicorn已安装')
        except ImportError:
            print('❌ uvicorn未安装，正在安装...')
            subprocess.check_call([sys.executable, "-m", "pip", "install", "uvicorn"])
        
        # 启动服务器
        print('启动服务器...')
        uvicorn_cmd = [
            sys.executable, "-m", "uvicorn", 
            "src.api.server:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ]
        
        print(f"执行命令: {' '.join(uvicorn_cmd)}")
        
        server_process = subprocess.Popen(
            uvicorn_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=PROJECT_ROOT
        )
        
        print(f"✅ 服务器进程启动成功，PID: {server_process.pid}")
        
        # 等待服务器启动
        print('等待服务器启动...')
        time.sleep(3)
        
        # 检查服务器是否还在运行
        if server_process.poll() is not None:
            print('❌ 服务器进程已终止')
            print(f"返回码: {server_process.returncode}")
            stdout = server_process.stdout.read()
            stderr = server_process.stderr.read()
            if stdout:
                print(f"标准输出:\n{stdout}")
            if stderr:
                print(f"错误输出:\n{stderr}")
            return False
        
        # 测试健康检查
        print('测试服务器健康检查...')
        try:
            with urllib.request.urlopen("http://localhost:8000/health", timeout=5) as response:
                data = response.read().decode('utf-8')
                result = json.loads(data)
                print(f"✅ 健康检查成功: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"❌ 健康检查失败: {str(e)}")
            raise e
        
        # 测试飞书配置
        print('测试飞书API配置...')
        try:
            with urllib.request.urlopen("http://localhost:8000/feishu/test", timeout=10) as response:
                data = response.read().decode('utf-8')
                result = json.loads(data)
                print(f"✅ 飞书配置测试成功: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"❌ 飞书配置测试失败: {str(e)}")
            raise e
        
        print()
        print('=== 服务器启动成功 ===')
        print()
        print('服务器正在运行:')
        print(f" 地址: http://localhost:8000")
        print(f" PID: {server_process.pid}")
        print()
        print('可以通过以下方式访问:')
        print(' 健康检查: http://localhost:8000/health')
        print(' 飞书配置: http://localhost:8000/feishu/test')
        print()
        print('按 Ctrl+C 停止服务器')
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print('正在停止服务器...')
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print('✅ 服务器已停止')
        
        return True
        
    except Exception as e:
        print(f"\n❌ 启动失败: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
