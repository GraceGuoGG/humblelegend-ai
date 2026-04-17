#!/usr/bin/env python3
"""
不依赖FastAPI的简单HTTP服务器
用于测试项目功能和API接口
"""

import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading

# 项目根路径
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

class SimpleAPIHandler(BaseHTTPRequestHandler):
    """简单的API请求处理程序"""
    
    def _send_response(self, status_code=200, data=None):
        """发送响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        if data is not None:
            self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self._send_response(200)
    
    def do_GET(self):
        """处理GET请求"""
        if self.path == '/health':
            self._send_response(200, {'status': 'healthy', 'message': 'HumbleLegend server is running'})
        elif self.path == '/':
            self._send_response(200, {'message': 'HumbleLegend API Service'})
        else:
            self._send_response(404, {'error': 'Not found'})
    
    def do_POST(self):
        """处理POST请求"""
        if self.path == '/process':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                
                print(f"收到原始数据: '{post_data}'")
                
                data = json.loads(post_data)
                
                user_id = data.get('user_id', 'default_user')
                input_text = data.get('input', '')
                
                print(f"解析参数 - user_id: '{user_id}', input: '{input_text}'")
                
                # 尝试加载核心应用
                from src.core.simple_app import SimpleHumbleLegendApp
                app = SimpleHumbleLegendApp()
                
                result = app.process(user_id, input_text)
                
                print(f"处理结果 - user_id: '{user_id}', input: '{input_text}', result: '{result}'")
                
                self._send_response(200, {'result': result})
                
            except Exception as e:
                import traceback
                self._send_response(500, {'error': str(e), 'traceback': traceback.format_exc()})
        
        elif self.path == '/feishu/events':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                
                print("收到飞书事件:", data)
                
                # 处理飞书事件
                from src.platforms.feishu_mock import FeishuAdapter
                adapter = FeishuAdapter({})
                
                result = adapter.handle_event({'headers': dict(self.headers), 'body': post_data})
                
                self._send_response(200, result)
                
            except Exception as e:
                import traceback
                self._send_response(500, {'error': str(e), 'traceback': traceback.format_exc()})
        
        else:
            self._send_response(404, {'error': 'Not found'})

def start_server(host='0.0.0.0', port=8000):
    """启动服务器"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, SimpleAPIHandler)
    
    print(f"服务器已启动: http://{host}:{port}")
    print("可用接口:")
    print("  GET  /")
    print("  GET  /health")
    print("  POST /process")
    print("  POST /feishu/events")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        httpd.shutdown()

if __name__ == "__main__":
    start_server()
