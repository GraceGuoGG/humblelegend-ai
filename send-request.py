#!/usr/bin/env python3
"""发送 HTTP 请求到 HumbleLegend 服务器"""

import socket
import json
import time

def send_request(host='localhost', port=8000, user_id='test_user', input_text=''):
    """发送 POST 请求到服务器"""
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        sock.connect((host, port))
        print(f"✅ 已连接到 {host}:{port}")
        
        # 准备请求数据
        data = {
            "user_id": user_id,
            "input": input_text
        }
        
        json_data = json.dumps(data, ensure_ascii=False)
        print(f"📝 请求数据: {json_data}")
        
        # 构建 HTTP 请求
        request = (
            f"POST /process HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Content-Type: application/json; charset=utf-8\r\n"
            f"Content-Length: {len(json_data.encode('utf-8'))}\r\n"
            f"User-Agent: Python/Test\r\n"
            f"\r\n"
            f"{json_data}"
        )
        
        sock.sendall(request.encode('utf-8'))
        
        # 等待响应
        time.sleep(0.5)
        
        # 接收响应
        response = sock.recv(4096).decode('utf-8')
        print(f"\n📨 服务器响应:")
        print(response)
        
        return True
        
    except ConnectionRefusedError:
        print(f"❌ 连接被拒绝，请确保服务器正在 {host}:{port} 上运行")
        return False
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        print(traceback.format_exc())
        return False
        
    finally:
        sock.close()

if __name__ == "__main__":
    print("=== HumbleLegend API 请求发送器 ===\n")
    
    # 测试用例
    user_input = input("请输入要记录的内容（默认为'帮我记录完成了项目报告'）: ")
    user_input = user_input.strip() or "帮我记录完成了项目报告"
    
    success = send_request(
        host='localhost',
        port=8000,
        user_id='test_user',
        input_text=user_input
    )
    
    print(f"\n{'✅ 请求成功' if success else '❌ 请求失败'}")