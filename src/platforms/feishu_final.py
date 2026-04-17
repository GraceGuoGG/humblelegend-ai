"""
飞书平台适配器（最终解决方案）
直接使用HTTP连接（如果HTTPS失败）
"""
import time
import json
import urllib.request
import urllib.parse
import urllib.error
import socket

from src.core.simple_app import SimpleHumbleLegendApp
from src.core.simple_database import SimpleDatabase
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FeishuAdapter:
    def __init__(self, config=None):
        self.config = config or {
            'app_id': 'cli_a955b0e8ad791bb4',
            'app_secret': 'Wvc7hHY2Gqe0Pks1wbXHCfFdjgPQlTXB',
            'verification_token': '',
            'encrypt_key': ''
        }
        self.app = SimpleHumbleLegendApp()
        self.db = SimpleDatabase()
        self._access_token = None
        self._token_expires_at = 0
        self.https_available = True

    def test_connection(self):
        logger.debug("测试网络连接...")
        try:
            sock = socket.create_connection(('open.feishu.cn', 443), timeout=5)
            sock.close()
            logger.debug("HTTPS连接成功")
            return True
        except Exception as e:
            logger.debug(f"HTTPS连接失败: {e}")
            self.https_available = False
            
            try:
                sock = socket.create_connection(('open.feishu.cn', 80), timeout=5)
                sock.close()
                logger.debug("HTTP连接成功")
                return True
            except Exception as e2:
                logger.debug(f"HTTP连接也失败: {e2}")
                return False

    def get_access_token(self):
        if self._access_token and time.time() < self._token_expires_at - 60:
            return self._access_token
        
        logger.debug("获取访问令牌...")
        
        if not self.test_connection():
            logger.debug("网络连接失败")
            return None
            
        try:
            if self.https_available:
                url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
            else:
                url = 'http://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
                
            logger.debug(f"使用URL: {url}")
            
            data = {
                "app_id": self.config['app_id'],
                "app_secret": self.config['app_secret']
            }
            logger.debug(f"请求数据: {data}")
            
            request_data = json.dumps(data).encode('utf-8')
            logger.debug(f"编码后数据长度: {len(request_data)}")
            
            req = urllib.request.Request(url, data=request_data)
            req.add_header('Content-Type', 'application/json')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            logger.debug("发送请求...")
            
            if self.https_available:
                import ssl
                context = ssl._create_unverified_context()
                
                with urllib.request.urlopen(req, context=context, timeout=10) as response:
                    logger.debug(f"响应状态: {response.getcode()}")
                    
                    if response.getcode() == 200:
                        raw_data = response.read()
                        logger.debug(f"响应数据长度: {len(raw_data)}")
                        
                        result = json.loads(raw_data.decode('utf-8'))
                        logger.debug(f"解码后数据: {result}")
                        
                        if result.get('code') == 0:
                            self._access_token = result['tenant_access_token']
                            self._token_expires_at = time.time() + result['expire']
                            logger.debug("访问令牌获取成功")
                            logger.debug(f"令牌有效期: {result['expire']}秒")
                            logger.debug(f"令牌前10字符: {self._access_token[:10]}")
                            return self._access_token
                        else:
                            logger.debug(f"获取失败: {result}")
                            return None
            else:
                with urllib.request.urlopen(req, timeout=10) as response:
                    logger.debug(f"响应状态: {response.getcode()}")
                    
                    if response.getcode() == 200:
                        raw_data = response.read()
                        logger.debug(f"响应数据长度: {len(raw_data)}")
                        
                        result = json.loads(raw_data.decode('utf-8'))
                        logger.debug(f"解码后数据: {result}")
                        
                        if result.get('code') == 0:
                            self._access_token = result['tenant_access_token']
                            self._token_expires_at = time.time() + result['expire']
                            logger.debug("访问令牌获取成功")
                            logger.debug(f"令牌有效期: {result['expire']}秒")
                            logger.debug(f"令牌前10字符: {self._access_token[:10]}")
                            return self._access_token
                        else:
                            logger.debug(f"获取失败: {result}")
                            return None
                            
        except ImportError as e:
            logger.debug(f"SSL导入失败: {e}")
            self.https_available = False
            
            try:
                url = 'http://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
                logger.debug(f"使用HTTP: {url}")
                
                req = urllib.request.Request(url, data=request_data)
                req.add_header('Content-Type', 'application/json')
                req.add_header('User-Agent', 'Mozilla/5.0')
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    logger.debug(f"响应状态: {response.getcode()}")
                    
                    if response.getcode() == 200:
                        raw_data = response.read()
                        logger.debug(f"响应数据长度: {len(raw_data)}")
                        
                        result = json.loads(raw_data.decode('utf-8'))
                        logger.debug(f"解码后数据: {result}")
                        
                        if result.get('code') == 0:
                            self._access_token = result['tenant_access_token']
                            self._token_expires_at = time.time() + result['expire']
                            logger.debug("访问令牌获取成功")
                            logger.debug(f"令牌前10字符: {self._access_token[:10]}")
                            return self._access_token
                        else:
                            logger.debug(f"获取失败: {result}")
                            return None
            except Exception as e2:
                logger.debug(f"HTTP请求也失败: {e2}")
                return None
                
        except Exception as e:
            logger.debug(f"其他异常: {type(e).__name__}: {e}")
            import traceback
            logger.debug(f"详情: {traceback.format_exc()}")
            return None
        
        return None

    def build_message_content(self, content):
        formatted = content.replace('# ', '').replace('## ', '').replace('### ', '')
        formatted = formatted.replace('[', '').replace(']', '').replace('(', '').replace(')', '')
        formatted = formatted.replace('![', '').replace(']', '')
        if '```mermaid' in formatted:
            formatted = formatted.split('```mermaid')[0]
        
        return {"text": formatted}

    def handle_command(self, user_id, command):
        logger.debug(f"处理命令: {command}")
        return self.app.process(user_id, command)

    def parse_message(self, event):
        try:
            if event.get('header', {}).get('event_type') == 'im.message.receive_v1':
                msg = event.get('event', {})
                user_id = msg.get('sender', {}).get('sender_id', {}).get('union_id', '')
                content = json.loads(msg.get('message', {}).get('content', '{}')).get('text', '')
                chat_type = msg.get('chat_type', 'p2p')
                return user_id, content, chat_type
        except Exception as e:
            logger.debug(f"解析消息失败: {e}")
        
        return None, None, None

    def handle_event(self, request):
        headers = request.get('headers', {})
        body = request.get('body', '')
        
        try:
            event = json.loads(body)
            user_id, content, chat_type = self.parse_message(event)
            
            if user_id and content:
                logger.debug(f"收到来自 {user_id} 的消息: {content}")
                
                result = self.handle_command(user_id, content)
                logger.debug(f"处理结果: {result}")
                
                return {'code': 0, 'msg': '成功'}
            else:
                logger.debug("无效的消息格式")
                return {'code': 2, 'msg': '无效的消息格式'}
                
        except Exception as e:
            logger.debug(f"处理事件失败: {e}")
            import traceback
            logger.debug(f"详情: {traceback.format_exc()}")
            return {'code': 1, 'msg': f'失败: {e}'}

def test_adapter():
    print("测试飞书适配器（最终解决方案）")
    try:
        config = {
            'app_id': 'cli_a955b0e8ad791bb4',
            'app_secret': 'Wvc7hHY2Gqe0Pks1wbXHCfFdjgPQlTXB'
        }
        adapter = FeishuAdapter(config)
        
        print("网络连接测试...")
        adapter.test_connection()
        
        print("SSL可用:", adapter.https_available)
        
        print("\n获取访问令牌...")
        token = adapter.get_access_token()
        if token:
            print(f"访问令牌获取成功: {token[:10]}...")
        else:
            print("访问令牌获取失败")
            
        print("\n处理命令测试...")
        result = adapter.handle_command('test_user', '帮我记录完成了项目报告')
        print(f"命令结果: {result}")
        
        return adapter
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    test_adapter()