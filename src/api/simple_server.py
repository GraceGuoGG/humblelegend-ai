"""
简单的HTTP服务器（无依赖）
使用Python标准库创建的HTTP服务器
支持飞书事件回调验证
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse

from src.core.simple_app import SimpleHumbleLegendApp
from src.platforms.feishu_fixed import FeishuAdapter

app_instance = SimpleHumbleLegendApp()
feishu_adapter = FeishuAdapter({
    'app_id': 'cli_a955b0e8ad791bb4',
    'app_secret': 'Wvc7hHY2Gqe0Pks1wbXHCfFdjgPQlTXB'
})

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """简单的HTTP请求处理器"""
    
    def _set_response(self, status_code=200, content_type='application/json'):
        """设置响应"""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self._set_response(200)
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/':
            self._set_response(200, 'text/plain')
            self.wfile.write(b"Welcome to HumbleLegend API!")
        elif parsed_path.path == '/health':
            self._set_response()
            self.wfile.write(json.dumps({'status': 'healthy'}).encode())
        elif parsed_path.path == '/feishu/test':
            try:
                token = feishu_adapter.get_access_token()
                self._set_response()
                self.wfile.write(json.dumps({
                    'token': '****' + token[-4:] if token else None,
                    'status': 'connected' if token else 'disconnected'
                }).encode())
            except Exception as e:
                self._set_response(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode())
    
    def do_POST(self):
        """处理POST请求"""
        parsed_path = urllib.parse.urlparse(self.path)
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            print("=== 收到POST请求 ===")
            print("路径: %s" % parsed_path.path)
            print("内容长度: %d" % content_length)
            decoded_data = post_data.decode('utf-8')
            
            if parsed_path.path == '/process':
                data = json.loads(decoded_data)
                
                user_id = data.get('user_id', 'default_user')
                input_text = data.get('input', '')
                
                result = app_instance.process(user_id, input_text)
                
                self._set_response()
                self.wfile.write(json.dumps({'result': result}).encode())
                
            elif parsed_path.path == '/feishu/events':
                # 解析请求数据
                try:
                    body_json = json.loads(decoded_data)
                except:
                    body_json = {}
                
                print("飞书事件数据: %s" % str(body_json)[:200])
                
                # 检查是否是 challenge 验证请求
                if 'challenge' in body_json:
                    # 飞书 URL 验证 - 返回 challenge 值
                    print("收到飞书challenge验证请求")
                    response_data = {
                        "challenge": body_json['challenge']
                    }
                    
                    self._set_response()
                    self.wfile.write(json.dumps(response_data).encode())
                    print("✅ Challenge验证响应已发送")
                else:
                    # 正常事件处理
                    result = feishu_adapter.handle_event({
                        'headers': dict(self.headers),
                        'body': decoded_data
                    })
                    
                    self._set_response()
                    self.wfile.write(json.dumps(result).encode())
                    print("事件处理结果: %s" % result)
                
            else:
                self._set_response(404)
                self.wfile.write(json.dumps({'error': 'Not Found'}).encode())
                
        except Exception as e:
            import traceback
            print("Error: %s" % traceback.format_exc())
            
            self._set_response(500)
            self.wfile.write(json.dumps({
                'error': str(e)
            }).encode())

def start_server(host='0.0.0.0', port=8000):
    """启动简单HTTP服务器"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    
    print("HumbleLegend API服务器启动")
    print("地址: http://%s:%d" % (host, port))
    print("可用接口:")
    print("  GET  /")
    print("  GET  /health")
    print("  GET  /feishu/test")
    print("  POST /process")
    print("  POST /feishu/events (支持飞书Challenge验证)")
    print("按 Ctrl+C 停止服务器")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器正在停止...")
        httpd.server_close()
        print("服务器已停止")

if __name__ == "__main__":
    start_server()
