"""
Feishu Platform Adapter (Fixed Version)
Handles Feishu message receiving, sending, and event callbacks
"""
import time
import json
import hashlib
import hmac
import base64
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../..')

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from src.core.simple_app import SimpleHumbleLegendApp
from src.core.simple_database import SimpleDatabase
import logging

disable_warnings(InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'app_id': '',
    'app_secret': '',
    'verification_token': '',
    'encrypt_key': ''
}


class FeishuAdapter:
    """Feishu Platform Adapter"""
    
    def __init__(self, config: dict = None):
        """Initialize"""
        self.config = config or DEFAULT_CONFIG
        self.app = SimpleHumbleLegendApp()
        self.db = SimpleDatabase()
        self._access_token = None
        self._token_expires_at = 0
        
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
        """Get access token"""
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
            response = self.session.post(url, headers=headers, json=body, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == 0:
                self._access_token = data['tenant_access_token']
                self._token_expires_at = time.time() + data['expire']
                logger.info(f"Successfully obtained access token: {self._access_token[:10]}...")
                return self._access_token
            else:
                logger.error(f"Failed to get access token: {data}")
                return None
        except Exception as e:
            logger.error(f"Exception getting access token: {str(e)}")
            return None
    
    def verify_event(self, headers: dict, body: str) -> bool:
        """Verify event callback authenticity"""
        if 'verification_token' not in self.config:
            return True
            
        request_token = headers.get('X-Lark-Request-Token')
        return request_token == self.config['verification_token']
    
    def decrypt_message(self, encrypt: str) -> dict:
        """Decrypt Feishu encrypted message"""
        if not self.config.get('encrypt_key'):
            return None
            
        try:
            pass
        except Exception as e:
            logger.error(f"Failed to decrypt message: {str(e)}")
            return None
    
    def parse_message(self, event: dict) -> tuple:
        """Parse Feishu message"""
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
            logger.error(f"Failed to parse message: {str(e)}")
        
        return None, None, None
    
    def handle_event(self, request: dict) -> dict:
        """Handle Feishu event"""
        logger.info("=== 收到飞书事件 ===")
        
        if not self.verify_event(request.get('headers', {}), request.get('body', '')):
            logger.error("事件验证失败")
            return {'code': 1, 'msg': 'Verification failed'}
        
        try:
            body = request.get('body', '{}')
            logger.info(f"原始body类型: {type(body)}")
            logger.info(f"原始body内容: {body[:200] if isinstance(body, str) else str(body)[:200]}...")
            
            if isinstance(body, str):
                try:
                    body = json.loads(body)
                    logger.info("JSON解析成功")
                except Exception as e:
                    logger.error(f"JSON parsing failed: {str(e)}")
                    return {'code': 2, 'msg': 'Invalid JSON format'}
            elif isinstance(body, dict):
                pass
            else:
                logger.error(f"Invalid body type: {type(body)}")
                return {'code': 2, 'msg': 'Invalid body type'}
            
            user_id, text_content, chat_type = self.parse_message(body)
            logger.info(f"解析结果 - user_id: {user_id}, text_content: {text_content}, chat_type: {chat_type}")
            
            if not user_id or not text_content:
                logger.warning("Invalid message format")
                return {'code': 2, 'msg': 'Invalid message format'}
            
            logger.info(f"处理用户消息 - user_id: {user_id}, message: {text_content}")
            
            result = self.app.process(user_id, text_content)
            logger.info(f"处理结果: {result[:100] if isinstance(result, str) else str(result)[:100]}...")
            
            self.send_reply(body, result)
            
            return {'code': 0, 'msg': 'Success'}
            
        except Exception as e:
            logger.error(f"Exception handling event: {str(e)}")
            import traceback
            logger.error("Detailed error: %s", traceback.format_exc())
            return {'code': 3, 'msg': f'Error: {str(e)}'}
    
    def send_reply(self, event: dict, content: str):
        """Send reply message"""
        try:
            message = event.get('event', {})
            message_id = message.get('message', {}).get('message_id', '')
            
            if not message_id:
                logger.warning("Missing message ID, cannot reply")
                return
            
            self.send_message(event, content)
            
        except Exception as e:
            logger.error(f"Failed to send reply: {str(e)}")
    
    def send_message(self, event: dict, content: str):
        """Send message"""
        try:
            token = self.get_access_token()
            if not token:
                logger.error("Failed to get access token")
                return
            
            message = event.get('event', {})
            
            reply_content = self.build_message_content(content)
            
            url = "https://open.feishu.cn/open-apis/im/v1/messages"
            params = {"receive_id_type": "open_id"}
            
            if event.get('event', {}).get('chat_type') == 'group':
                url = "https://open.feishu.cn/open-apis/im/v1/messages"
                params = {"receive_id_type": "chat_id"}
                data = {
                    "receive_id": event.get('event', {}).get('message', {}).get('chat_id'),
                    "msg_type": "text",
                    "content": json.dumps(reply_content)
                }
            else:
                # 私聊消息
                sender_id = event.get('event', {}).get('sender', {}).get('sender_id', {})
                receive_id = sender_id.get('open_id', '') or sender_id.get('user_id', '') or sender_id.get('union_id', '')
                
                if not receive_id:
                    logger.warning("无法获取发送者ID")
                    return
                    
                data = {
                    "receive_id": receive_id,
                    "msg_type": "text",
                    "content": json.dumps(reply_content)
                }
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(url, params=params, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') == 0:
                logger.info("Message sent successfully")
            else:
                logger.error(f"Failed to send message: {result}")
            
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            import traceback
            logger.error("Detailed error: %s", traceback.format_exc())
    
    def build_message_content(self, content: str) -> dict:
        """Build Feishu message content"""
        formatted_content = content
        
        formatted_content = formatted_content.replace('# ', '')
        formatted_content = formatted_content.replace('## ', '')
        formatted_content = formatted_content.replace('### ', '')
        
        formatted_content = formatted_content.replace('[', '').replace(']', '')
        formatted_content = formatted_content.replace('(', '').replace(')', '')
        
        formatted_content = formatted_content.replace('![', '').replace(']', '')
        
        if '```mermaid' in formatted_content:
            formatted_content = formatted_content.split('```mermaid')[0]
        
        return {
            "text": formatted_content
        }
    
    def handle_command(self, user_id: str, command: str) -> str:
        """Handle Feishu command"""
        logger.info(f"Handling command for user {user_id}: {command}")
        
        return self.app.process(user_id, command)


def main():
    """Feishu platform main function"""
    config = {
        'app_id': 'cli_a955b0e8ad791bb4',
        'app_secret': 'Wvc7hHY2Gqe0Pks1wbXHCfFdjgPQlTXB',
        'verification_token': '',
        'encrypt_key': ''
    }
    
    adapter = FeishuAdapter(config)
    
    print("Feishu adapter initialized!")
    print("Getting access token...")
    token = adapter.get_access_token()
    
    if token:
        print("Access token obtained")
        print(f"Token first 10 chars: {token[:10]}...")
    else:
        print("Failed to get access token")
        return
    
    print("\nFeishu platform adapter ready to receive messages.")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            user_input = input("\nEnter command (or 'exit' to quit): ").strip()
            if user_input.lower() == 'exit':
                break
                
            result = adapter.handle_command("local_user", user_input)
            print("\nAI Response:")
            print(result)
    except KeyboardInterrupt:
        print("\nService stopped")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
