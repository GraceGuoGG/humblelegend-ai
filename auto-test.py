#!/usr/bin/env python3
"""自动化测试脚本 - 直接发送请求"""

import socket
import json
import time

def send_request(host='localhost', port=8000, user_id='test_user', input_text=''):
    """发送 POST 请求到服务器"""
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        sock.connect((host, port))
        
        data = {
            "user_id": user_id,
            "input": input_text
        }
        
        json_data = json.dumps(data, ensure_ascii=False)
        
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
        
        time.sleep(0.5)
        
        response = sock.recv(4096).decode('utf-8')
        
        return response
        
    except Exception as e:
        return f"Error: {e}"
        
    finally:
        sock.close()

if __name__ == "__main__":
    print("=== HumbleLegend API 自动化测试 ===")
    
    test_inputs = [
        '帮我记录完成了项目报告',
        '记录项目报告',
        '帮我记录'
    ]
    
    for text in test_inputs:
        print(f"\n{'='*50}")
        print(f"测试输入: '{text}'")
        print(f"{'='*50}")
        
        response = send_request(
            host='localhost',
            port=8000,
            user_id='test_user',
            input_text=text
        )
        
        if response.startswith('Error'):
            print(response)
        else:
            print("服务器响应:")
            print(response)