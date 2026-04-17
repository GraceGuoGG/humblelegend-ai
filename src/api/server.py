"""HTTP API服务（简化版）"""

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="HumbleLegend API",
    description="HumbleLegend AI Agent API",
    version="1.0.0"
)

# 初始化简单应用
from src.core.simple_app import SimpleHumbleLegendApp
app_instance = SimpleHumbleLegendApp()

# 配置使用模拟适配器
from src.platforms.feishu_mock import FeishuAdapter

feishu_config = {
    'app_id': os.getenv('FEISHU_APP_ID', 'cli_a955b0e8ad791bb4'),
    'app_secret': os.getenv('FEISHU_APP_SECRET', 'Wvc7hHY2Gqe0Pks1wbXHCfFdjgPQlTXB'),
    'verification_token': os.getenv('FEISHU_VERIFICATION_TOKEN', ''),
    'encrypt_key': os.getenv('FEISHU_ENCRYPT_KEY', '')
}

feishu_adapter = FeishuAdapter(feishu_config)
print("✅ 使用模拟的飞书适配器（无SSL需求）")

# 请求模型
class ProcessRequest(BaseModel):
    input: str
    user_id: str = "default_user"

# 响应模型
class Response(BaseModel):
    result: str

@app.post("/process", response_model=Response)
async def process(request: ProcessRequest):
    """处理用户输入"""
    try:
        result = app_instance.process(request.user_id, request.input)
        return Response(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feishu/events")
async def feishu_events(request: Request):
    """处理飞书事件"""
    try:
        # 获取请求头和请求体
        headers = dict(request.headers)
        body = await request.body()
        
        print(f"收到请求: {headers.get('User-Agent', 'Unknown')}")
        print(f"请求体长度: {len(body)}字节")
        
        # 处理事件
        result = feishu_adapter.handle_event({
            'headers': headers,
            'body': body.decode('utf-8')
        })
        
        return result
    except Exception as e:
        import traceback
        print(f"Error handling feishu event: {traceback.format_exc()}")
        return {'code': 500, 'msg': str(e)}

@app.get("/")
async def root():
    """根路径"""
    return {"message": "HumbleLegend API Service"}

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}

@app.get("/feishu/test")
async def feishu_test():
    """飞书配置测试"""
    try:
        token = feishu_adapter.get_access_token()
        return {
            'token': '****' + token[-4:] if token else None,
            'status': 'connected' if token else 'disconnected',
            'config': {
                'app_id': feishu_adapter.config['app_id'],
                'verification_token': feishu_adapter.config['verification_token'][:5] + '****' if feishu_adapter.config['verification_token'] else None
            }
        }
    except Exception as e:
        return {
            'token': None,
            'status': 'error',
            'error': str(e)
        }

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """启动服务器"""
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()