"""
飞书平台适配器（最简单版本）
完全使用urllib，无复杂缩进
"""
import time
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl

from src.core.simple_app import SimpleHumbleLegendApp
from src.core.simple_database import SimpleDatabase
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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

    def get_access_token(self):
        if self._access_token and time.time() < self._token_expires_at - 60:
            return self._access_token
        
        logger.info("获取访问令牌...")
        
        try:
            context = ssl._create_unverified_context()
            url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
            data = json.dumps({
                "app_id": self.config['app_id'],
                "app_secret": self.config['app_secret']
            }).encode('utf-8')
            
            req = urllib.request.Request(url, data=data)
            req.add_header('Content-Type', 'application/json')
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(req, context=context, timeout=10) as response:
                if response.getcode() == 200:
                    result = json.loads(response.read().decode('utf-8'))
                    logger.info(f"响应: {str(result)[:200]}")
                    
                    if result.get('code') == 0:
                        self._access_token = result['tenant_access_token']
                        self._token_expires_at = time.time() + result['expire']
                        logger.info("访问令牌获取成功")
                        return self._access_token
                    else:
                        logger.error(f"获取失败: {result}")
                        return None
        except Exception as e:
            logger.error(f"异常: {e}")
            return None
        
        return None

    def send_message(self, event, content):
        token = self.get_access_token()
        if not token:
            logger.error("无访问令牌")
            return
            
        logger.info("发送消息...")
        
        try:
            context = ssl._create_unverified_context()
            
            message_content = self.build_message_content(content)
            
            data = {
                "msg_type": "text",
                "content": json.dumps(message_content)
            }
            
            chat_type = event.get('event', {}).get('chat_type', 'p2p')
            if chat_type == 'group':
                data["receive_id"] = event.get('event', {}).get('message', {}).get('chat_id')
                url = 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id'
            else:
                data["receive_id"] = event.get('event', {}).get('sender', {}).get('sender_id', {}).get('open_id', '')
                url = 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id'
            
            req = urllib.request.Request(url, json.dumps(data).encode('utf-8'))
            req.add_header('Authorization', f'Bearer {token}')
            req.add_header('Content-Type', 'application/json')
            
            with urllib.request.urlopen(req, context=context, timeout=10) as response:
                if response.getcode() == 200:
                    logger.info("消息发送成功")
                else:
                    logger.error(f"发送失败: {response.getcode()}")
        except Exception as e:
            logger.error(f"发送异常: {e}")

    def build_message_content(self, content):
        formatted = content.replace('# ', '').replace('## ', '').replace('### ', '')
        formatted = formatted.replace('[', '').replace(']', '').replace('(', '').replace(')', '')
        formatted = formatted.replace('![', '').replace(']', '')
        if '```mermaid' in formatted:
            formatted = formatted.split('```mermaid')[0]
        
        return {"text": formatted}

    def handle_command(self, user_id, command):
        logger.info(f"处理命令: {command}")
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
            logger.error(f"解析消息失败: {e}")
        
        return None, None, None

    def handle_event(self, request):
        headers = request.get('headers', {})
        body = request.get('body', '')
        
        try:
            event = json.loads(body)
            user_id, content, chat_type = self.parse_message(event)
            
            if user_id and content:
                logger.info(f"收到来自 {user_id} 的消息: {content}")
                
                result = self.handle_command(user_id, content)
                self.send_message(event, result)
                
                return {'code': 0, 'msg': '成功'}
            else:
                logger.warning("无效的消息格式")
                return {'code': 2, 'msg': '无效的消息格式'}
                
        except Exception as e:
            logger.error(f"处理事件失败: {e}")
            return {'code': 1, 'msg': f'失败: {e}'}

def test_adapter():
    print("测试飞书适配器")
    try:
        config = {
            'app_id': 'cli_a955b0e8ad791bb4',
            'app_secret': 'Wvc7hHY2Gqe0Pks1wbXHCfFdjgPQlTXB'
        }
        adapter = FeishuAdapter(config)
        
        token = adapter.get_access_token()
        if token:
            print(f"访问令牌获取成功: {token[:10]}...")
        else:
            print("访问令牌获取失败")
            
        result = adapter.handle_command('test_user', '帮我记录完成了项目报告')
        print(f"处理命令: {result}")
        
        return adapter
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    test_adapter()