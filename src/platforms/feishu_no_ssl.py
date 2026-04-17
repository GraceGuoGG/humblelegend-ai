"""
飞书平台适配器（跳过SSL验证版本）
用于解决网络连接问题的临时版本
"""
import time
import json
import hashlib
import hmac
import base64
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../..')

# 导入必要的模块，但跳过SSL验证
try:
    import urllib3
    urllib3.disable_warnings()
except ImportError:
    pass

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    from urllib3 import disable_warnings
    from urllib3.exceptions import InsecureRequestWarning
    disable_warnings(InsecureRequestWarning)
except ImportError as e:
    print(f"Requests模块导入失败: {e}")
    sys.exit(1)

from src.core.simple_app import SimpleHumbleLegendApp
from src.core.simple_database import SimpleDatabase
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_CONFIG = {
    'app_id': '',
    'app_secret': '',
    'verification_token': '',
    'encrypt_key': ''
}


class FeishuAdapter:
    """飞书平台适配器（跳过SSL验证）"""
    
    def __init__(self, config: dict = None):
        """初始化"""
        self.config = config or DEFAULT_CONFIG
        self.app = SimpleHumbleLegendApp()
        self.db = SimpleDatabase()
        self._access_token = None
        self._token_expires_at = 0
        
        # 创建会话对象，完全跳过SSL验证
        self.session = requests.Session()
        self.session.verify = False
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount('https://', adapter)
    
    def get_access_token(self) -> str:
        """获取访问令牌（跳过SSL验证）"""
        if self._access_token and time.time() < self._token_expires_at - 60:
            return self._access_token
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {
            "Content-Type": "application/json"
        }
        body = {
            "app_id": self.config['app_id'],
            "app_secret": self.config['app_secret']
        }
        
        try:
            logger.info("正在尝试获取飞书访问令牌...")
            response = self.session.post(url, headers=headers, json=body, timeout=10)
            logger.info("响应状态码: %d", response.status_code)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("响应内容: %s", str(data)[:200])
                if data.get('code') == 0:
                    self._access_token = data['tenant_access_token']
                    self._token_expires_at = time.time() + data['expire']
                    logger.info("访问令牌获取成功，有效期: %d秒", data['expire'])
                    return self._access_token
                else:
                    logger.error("获取访问令牌失败: %s", data)
                    return None
            else:
                logger.error("HTTP请求失败: %d %s", response.status_code, response.reason)
                return None
        except Exception as e:
            logger.error("获取访问令牌异常: %s", str(e))
            import traceback
            logger.error("详细错误信息: %s", traceback.format_exc())
            return None
    
    def verify_event(self, headers: dict, body: str) -> bool:
        """验证事件回调的真实性"""
        if 'verification_token' not in self.config:
            return True
            
        request_token = headers.get('X-Lark-Request-Token')
        return request_token == self.config['verification_token']
    
    def decrypt_message(self, encrypt: str) -> dict:
        """解密飞书加密消息"""
        if not self.config.get('encrypt_key'):
            return None
            
        try:
            # 飞书加密消息解密逻辑
            pass
        except Exception as e:
            logger.error(f"解密消息失败: {str(e)}")
            return None
    
    def parse_message(self, event: dict) -> tuple:
        """解析飞书消息"""
        try:
            event_type = event.get('header', {}).get('event_type')
            
            if event_type == 'im.message.receive_v1':
                message = event.get('event', {})
                sender = message.get('sender', {})
                user_id = sender.get('sender_id', {}).get('union_id', '')
                
                message_body = message.get('message', {})
                content = json.loads(message_body.get('content', '{}'))
                text_content = content.get('text', '')
                
                chat_type = message.get('chat_type', 'p2p')
                
                return user_id, text_content, chat_type
                
        except Exception as e:
            logger.error(f"解析消息失败: {str(e)}")
        
        return None, None, None
    
    def handle_event(self, request: dict) -> dict:
        """处理飞书事件"""
        # 验证事件
        if not self.verify_event(request.get('headers', {}), request.get('body', '')):
            return {'code': 1, 'msg': '验证失败'}
        
        try:
            # 解析事件
            body = json.loads(request.get('body', '{}'))
            user_id, text_content, chat_type = self.parse_message(body)
            
            if not user_id or not text_content:
                logger.warning("无效的消息格式")
                return {'code': 2, 'msg': '无效的消息格式'}
            
            logger.info(f"收到来自用户 {user_id} 的消息: {text_content}")
            
            # 处理用户请求
            result = self.app.process(user_id, text_content)
            
            # 发送回复
            self.send_reply(body, result)
            
            return {'code': 0, 'msg': '处理成功'}
            
        except Exception as e:
            logger.error(f"处理事件异常: {str(e)}")
            import traceback
            logger.error("详细错误信息: %s", traceback.format_exc())
            return {'code': 3, 'msg': f'处理异常: {str(e)}'}
    
    def send_reply(self, event: dict, content: str):
        """发送回复消息"""
        try:
            message = event.get('event', {})
            message_id = message.get('message', {}).get('message_id', '')
            
            if not message_id:
                logger.warning("缺少消息ID，无法回复")
                return
            
            # 发送回复
            self.send_message(event, content)
            
        except Exception as e:
            logger.error(f"发送回复失败: {str(e)}")
    
    def send_message(self, event: dict, content: str):
        """发送消息"""
        try:
            token = self.get_access_token()
            if not token:
                logger.error("获取访问令牌失败")
                return
            
            message = event.get('event', {})
            
            # 构建消息内容
            reply_content = self.build_message_content(content)
            
            url = "https://open.feishu.cn/open-apis/im/v1/messages"
            params = {"receive_id_type": "open_id"}
            
            # 根据消息类型决定发送目标
            if event.get('event', {}).get('chat_type') == 'group':
                # 群聊消息
                url = "https://open.feishu.cn/open-apis/im/v1/messages"
                params = {"receive_id_type": "chat_id"}
                data = {
                    "receive_id": event.get('event', {}).get('message', {}).get('chat_id'),
                    "msg_type": "text",
                    "content": json.dumps(reply_content)
                }
            else:
                # 私聊消息
                data = {
                    "receive_id": event.get('event', {}).get('sender', {}).get('sender_id', {}).get('open_id', ''),
                    "msg_type": "text",
                    "content": json.dumps(reply_content)
                }
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(url, params=params, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            logger.info("消息发送成功")
            
        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}")
    
    def build_message_content(self, content: str) -> dict:
        """构建飞书消息内容"""
        # 对内容进行格式化，去除Markdown标记（如果有）
        formatted_content = content
        
        # 去除Markdown标题
        formatted_content = formatted_content.replace('# ', '')
        formatted_content = formatted_content.replace('## ', '')
        formatted_content = formatted_content.replace('### ', '')
        
        # 去除Markdown链接
        formatted_content = formatted_content.replace('[', '').replace(']', '')
        formatted_content = formatted_content.replace('(', '').replace(')', '')
        
        # 去除Markdown图片语法
        formatted_content = formatted_content.replace('![', '').replace(']', '')
        
        # 去除Mermaid图表
        if '```mermaid' in formatted_content:
            formatted_content = formatted_content.split('```mermaid')[0]
        
        return {
            "text": formatted_content
        }
    
    def handle_command(self, user_id: str, command: str) -> str:
        """处理飞书命令"""
        logger.info(f"处理用户 {user_id} 的命令: {command}")
        
        return self.app.process(user_id, command)


def test_adapter():
    """测试飞书适配器"""
    print("测试飞书适配器")
    
    config = {
        'app_id': 'cli_a955b0e8ad791bb4',
        'app_secret': 'Wvc7hHY2Gqe0Pks1wbXHCfFdjgPQlTXB',
        'verification_token': '',
        'encrypt_key': ''
    }
    
    try:
        print("创建适配器实例...")
        adapter = FeishuAdapter(config)
        
        print("获取访问令牌...")
        token = adapter.get_access_token()
        
        if token:
            print(f"访问令牌获取成功，长度: {len(token)}字符")
            print(f"令牌前缀: {token[:10]}...")
        else:
            print("访问令牌获取失败")
            
        return adapter
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        print(traceback.format_exc())
        return None


if __name__ == "__main__":
    test_adapter()