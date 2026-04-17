"""
HTTP API路由
FastAPI实现RESTful接口
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from loguru import logger

from ..agents.orchestrator import OrchestratorAgent
from ..core.config import load_config


app = FastAPI(
    title="HumbleLegend API",
    description="轻量级AI助手API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator: Optional[OrchestratorAgent] = None


class ProcessRequest(BaseModel):
    input: str
    user_id: str = "default_user"
    attachments: Optional[List[Dict[str, Any]]] = None


class ProcessResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    needs_confirmation: bool = False
    record_id: Optional[int] = None


class SettingsResponse(BaseModel):
    topics: List[Dict[str, str]]
    nutrition_goal: Dict[str, float]
    sleep_goal: Dict[str, str]
    water_goal: Dict[str, int]


@app.on_event("startup")
async def startup_event():
    global orchestrator
    config = load_config()
    orchestrator = OrchestratorAgent(config)
    logger.info("API服务启动完成")


@app.get("/")
async def root():
    return {"message": "HumbleLegend API", "version": "1.0.0"}


@app.post("/process", response_model=ProcessResponse)
async def process(request: ProcessRequest):
    if not orchestrator:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    response = orchestrator.process(
        request.input,
        request.user_id,
        request.attachments
    )
    
    return ProcessResponse(
        success=response.success,
        message=response.message,
        data=response.data,
        needs_confirmation=response.needs_confirmation,
        record_id=response.record_id,
    )


@app.get("/settings", response_model=SettingsResponse)
async def get_settings():
    if not orchestrator:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    settings = orchestrator.settings.get_all_settings()
    
    return SettingsResponse(
        topics=settings["topics"],
        nutrition_goal=settings["nutrition_goal"],
        sleep_goal=settings["sleep_goal"],
        water_goal=settings["water_goal"],
    )


@app.post("/settings/topics")
async def add_topic(name: str, description: str = ""):
    if not orchestrator:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    result = orchestrator.settings.add_topic(name, description)
    return result


@app.delete("/settings/topics/{name}")
async def remove_topic(name: str):
    if not orchestrator:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    result = orchestrator.settings.remove_topic(name)
    return result


@app.get("/daily-report/today")
async def get_today_report(user_id: str = "default_user", with_chart: bool = False):
    if not orchestrator:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    result = orchestrator.daily_report.generate_today_report(user_id, with_chart)
    return result


@app.get("/daily-report/{date}")
async def get_report(date: str, user_id: str = "default_user"):
    if not orchestrator:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    result = orchestrator.daily_report.generate_report(user_id, date)
    return result


@app.get("/review/{topic}")
async def get_review(topic: str, user_id: str = "default_user"):
    if not orchestrator:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    result = orchestrator.review.generate_review(user_id, topic)
    return result


@app.get("/memory")
async def get_memory(user_id: str = "default_user"):
    if not orchestrator:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    result = orchestrator.memory.get_all_memories(user_id)
    return result


@app.delete("/memory")
async def clear_memory(user_id: str = "default_user", memory_type: Optional[str] = None):
    if not orchestrator:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    result = orchestrator.memory.clear_memories(user_id, memory_type)
    return result


@app.get("/suggestions")
async def get_suggestions():
    if not orchestrator:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    return {"suggestions": orchestrator.get_command_suggestions()}


@app.post("/wechat/webhook")
async def wechat_webhook(request: Request):
    from ..platforms.wechat import WeChatPlatform
    
    if not orchestrator:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    body = await request.body()
    
    from xml.etree import ElementTree
    try:
        xml_data = ElementTree.fromstring(body)
        message = {child.tag: child.text for child in xml_data}
    except Exception as e:
        logger.error(f"解析微信消息失败: {e}")
        raise HTTPException(status_code=400, detail="无效的XML格式")
    
    wechat = WeChatPlatform(orchestrator.config)
    response = wechat.handle_message(message)
    
    from xml.etree.ElementTree import tostring
    xml_response = tostring(
        ElementTree.Element("xml", attrib={k: str(v) for k, v in response.items()}),
        encoding="unicode"
    )
    
    return JSONResponse(content=xml_response, media_type="application/xml")


@app.post("/feishu/webhook")
async def feishu_webhook(event: Dict[str, Any]):
    from ..platforms.feishu import FeishuPlatform
    
    if not orchestrator:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    feishu = FeishuPlatform(orchestrator.config)
    response = feishu.handle_message(event)
    
    return response


def run_api(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run(app, host=host, port=port)
