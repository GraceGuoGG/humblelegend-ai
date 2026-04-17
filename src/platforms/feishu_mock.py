"""
飞书平台适配器（模拟响应）
完全不使用网络连接，直接返回模拟数据
"""
import time
import json
import logging

from src.core.simple_app import SimpleHumbleLegendApp
from src.core.simple_database import SimpleDatabase

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
        self._access_token = 'mock_access_token_1234567890'
        self._token_expires_at = time.time() + 7200
        logger.debug("适配器初始化完成（使用模拟数据）")

    def test_connection(self):
        logger.debug("测试网络连接（模拟）")
        return True

    def get_access_token(self):
        logger.debug("获取访问令牌（模拟）")
        if self._access_token and time.time() < self._token_expires_at - 60:
            return self._access_token
        
        logger.debug("重新获取模拟访问令牌")
        self._access_token = 'mock_access_token_' + str(int(time.time()))
        self._token_expires_at = time.time() + 7200
        
        return self._access_token

    def send_message(self, event, content):
        logger.debug(f"发送消息（模拟）: {content}")
        
        # 这里不发送真实消息，只记录日志
        logger.debug(f"模拟向 {event.get('event', {}).get('chat_type', 'p2p')} 发送消息")
        logger.debug(f"消息内容: {content}")
        
        return True

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
            
            # 处理飞书验证事件
            if event.get('header', {}).get('event_type') == 'url_verification':
                challenge = event.get('event', {}).get('challenge')
                logger.debug(f"收到验证挑战: {challenge}")
                return {'challenge': challenge}
                
            # 处理消息事件
            user_id, content, chat_type = self.parse_message(event)
            
            if user_id and content:
                logger.debug(f"收到来自 {user_id} 的消息: {content}")
                
                result = self.handle_command(user_id, content)
                self.send_message(event, result)
                
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
    print("测试飞书适配器（模拟响应）")
    try:
        config = {
            'app_id': 'cli_a955b0e8ad791bb4',
            'app_secret': 'Wvc7hHY2Gqe0Pks1wbXHCfFdjgPQlTXB'
        }
        adapter = FeishuAdapter(config)
        
        print("网络连接测试...")
        print("网络连接:", adapter.test_connection())
        
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