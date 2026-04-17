"""
主调度Agent
接收用户输入，解析指令，分发任务，协调各子Agent执行，返回最终结果
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

from ..core.config import Config, load_config
from ..core.database import init_database
from .parser import ParserAgent, ParsedCommand, IntentType
from .record import RecordAgent, RecordResult
from .calorie import CalorieAgent
from .polish import PolishAgent
from .collect import CollectAgent
from .daily_report import DailyReportAgent
from .review import ReviewAgent
from .settings import SettingsAgent
from .memory import MemoryAgent


@dataclass
class AgentResponse:
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    needs_confirmation: bool = False
    record_id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "needs_confirmation": self.needs_confirmation,
            "record_id": self.record_id,
        }


class OrchestratorAgent:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or load_config()
        init_database(self.config.database_path)
        
        self.parser = ParserAgent()
        self.memory = MemoryAgent(self.config, self.config.database_path)
        self.record = RecordAgent(self.config, self.config.database_path)
        self.calorie = CalorieAgent(self.config)
        self.polish = PolishAgent(self.config)
        self.collect = CollectAgent(self.config)
        self.daily_report = DailyReportAgent(self.config, self.config.database_path)
        self.review = ReviewAgent(self.config, self.config.database_path)
        self.settings = SettingsAgent(self.config)
        
        self.parser.set_memory_agent(self.memory)
        
        self._pending_confirmations: Dict[str, Dict[str, Any]] = {}
        
        logger.info("OrchestratorAgent初始化完成")
    
    def process(
        self,
        user_input: str,
        user_id: str = "default_user",
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> AgentResponse:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if self._is_confirmation(user_input, user_id):
            return self._handle_confirmation(user_input, user_id)
        
        if self._is_modification(user_input, user_id):
            return self._handle_modification(user_input, user_id)
        
        command = self.parser.parse(user_input, attachments)
        
        return self._dispatch(command, user_id, timestamp)
    
    def _dispatch(self, command: ParsedCommand, user_id: str, timestamp: str) -> AgentResponse:
        intent = command.intent
        
        if intent == IntentType.RECORD_DAILY:
            return self._handle_record_daily(command, user_id)
        
        elif intent == IntentType.RECORD_CALORIE:
            return self._handle_record_calorie(command, user_id)
        
        elif intent == IntentType.COLLECT:
            return self._handle_collect(command, user_id)
        
        elif intent == IntentType.POLISH:
            return self._handle_polish(command, user_id)
        
        elif intent == IntentType.DAILY_REPORT_TODAY:
            return self._handle_daily_report_today(command, user_id)
        
        elif intent == IntentType.DAILY_REPORT_HISTORY:
            return self._handle_daily_report_history(command, user_id)
        
        elif intent == IntentType.REVIEW:
            return self._handle_review(command, user_id)
        
        elif intent == IntentType.SETTINGS:
            return self._handle_settings(command, user_id)
        
        elif intent == IntentType.MEMORY_CLEAR:
            return self._handle_memory_clear(command, user_id)
        
        elif intent == IntentType.MEMORY_QUERY:
            return self._handle_memory_query(command, user_id)
        
        else:
            return AgentResponse(
                success=False,
                message="无法识别您的指令，请使用以下格式：\n" + "\n".join(self.parser.get_command_suggestions()),
            )
    
    def _handle_record_daily(self, command: ParsedCommand, user_id: str) -> AgentResponse:
        result = self.record.execute(command, user_id)
        
        if result.success and result.needs_confirmation:
            self._pending_confirmations[user_id] = {
                "type": "record",
                "record_id": result.record_id,
                "record_type": result.record_type,
            }
        
        return AgentResponse(
            success=result.success,
            message=result.message,
            data=result.to_dict(),
            needs_confirmation=result.needs_confirmation,
            record_id=result.record_id,
        )
    
    def _handle_record_calorie(self, command: ParsedCommand, user_id: str) -> AgentResponse:
        result = self.record.execute(command, user_id)
        
        if result.success and result.needs_confirmation:
            self._pending_confirmations[user_id] = {
                "type": "record",
                "record_id": result.record_id,
                "record_type": result.record_type,
            }
        
        return AgentResponse(
            success=result.success,
            message=result.message,
            data=result.to_dict(),
            needs_confirmation=result.needs_confirmation,
            record_id=result.record_id,
        )
    
    def _handle_collect(self, command: ParsedCommand, user_id: str) -> AgentResponse:
        result = self.record.execute(command, user_id)
        
        if result.success and result.needs_confirmation:
            self._pending_confirmations[user_id] = {
                "type": "record",
                "record_id": result.record_id,
                "record_type": result.record_type,
            }
        
        return AgentResponse(
            success=result.success,
            message=result.message,
            data=result.to_dict(),
            needs_confirmation=result.needs_confirmation,
            record_id=result.record_id,
        )
    
    def _handle_polish(self, command: ParsedCommand, user_id: str) -> AgentResponse:
        result = self.record.execute(command, user_id)
        
        if result.success and result.needs_confirmation:
            self._pending_confirmations[user_id] = {
                "type": "record",
                "record_id": result.record_id,
                "record_type": result.record_type,
            }
        
        return AgentResponse(
            success=result.success,
            message=result.message,
            data=result.to_dict(),
            needs_confirmation=result.needs_confirmation,
            record_id=result.record_id,
        )
    
    def _handle_daily_report_today(self, command: ParsedCommand, user_id: str) -> AgentResponse:
        with_chart = command.params.get("with_chart", False)
        result = self.daily_report.generate_today_report(user_id, with_chart)
        
        return AgentResponse(
            success=result.get("success", False),
            message=result.get("content", result.get("message", "日报生成失败")),
            data=result,
        )
    
    def _handle_daily_report_history(self, command: ParsedCommand, user_id: str) -> AgentResponse:
        date = command.params.get("date") or command.content
        result = self.daily_report.generate_report(user_id, date)
        
        return AgentResponse(
            success=result.get("success", False),
            message=result.get("content", result.get("message", "日报生成失败")),
            data=result,
        )
    
    def _handle_review(self, command: ParsedCommand, user_id: str) -> AgentResponse:
        topic = command.content
        result = self.review.generate_review(user_id, topic)
        
        return AgentResponse(
            success=result.get("success", False),
            message=result.get("content", result.get("message", "复盘报告生成失败")),
            data=result,
        )
    
    def _handle_settings(self, command: ParsedCommand, user_id: str) -> AgentResponse:
        result = self.settings.process_natural_language(command.raw_input)
        
        return AgentResponse(
            success=result.get("success", False),
            message=result.get("message", "设置失败"),
            data=result,
        )
    
    def _handle_memory_clear(self, command: ParsedCommand, user_id: str) -> AgentResponse:
        result = self.memory.clear_memories(user_id)
        
        return AgentResponse(
            success=result.get("success", False),
            message=result.get("message", "清除记忆失败"),
            data=result,
        )
    
    def _handle_memory_query(self, command: ParsedCommand, user_id: str) -> AgentResponse:
        result = self.memory.get_all_memories(user_id)
        
        message = f"""记忆统计：
- 总记录数：{result['total_count']}/{result['limit']}
- 指令缩写：{result['command_shortcuts']}条
- 主题偏好：{result['topic_preferences']}条
- 输出偏好：{result['output_preferences']}条"""
        
        return AgentResponse(
            success=True,
            message=message,
            data=result,
        )
    
    def _is_confirmation(self, user_input: str, user_id: str) -> bool:
        confirmation_keywords = ["确认", "不用改", "没问题", "好的", "OK", "ok", "是", "对"]
        return any(kw in user_input for kw in confirmation_keywords) and user_id in self._pending_confirmations
    
    def _handle_confirmation(self, user_input: str, user_id: str) -> AgentResponse:
        pending = self._pending_confirmations.pop(user_id)
        
        if pending["type"] == "record":
            self.record.confirm_record(pending["record_id"])
            
            return AgentResponse(
                success=True,
                message="已确认并保存记录。",
                data={"record_id": pending["record_id"]},
            )
        
        return AgentResponse(
            success=True,
            message="已确认。",
        )
    
    def _is_modification(self, user_input: str, user_id: str) -> bool:
        modification_keywords = ["修改", "改成", "换成", "不对", "错了"]
        return any(kw in user_input for kw in modification_keywords) and user_id in self._pending_confirmations
    
    def _handle_modification(self, user_input: str, user_id: str) -> AgentResponse:
        pending = self._pending_confirmations.get(user_id)
        
        if not pending:
            return AgentResponse(
                success=False,
                message="没有待修改的记录。",
            )
        
        modifications = {}
        
        if "内容" in user_input or "改成" in user_input:
            import re
            match = re.search(r"(?:内容|改成)[：:]*\s*(.+?)(?:\s|$)", user_input)
            if match:
                modifications["content"] = match.group(1).strip()
        
        if "主题" in user_input:
            import re
            match = re.search(r"主题[：:]*\s*(.+?)(?:\s|$)", user_input)
            if match:
                topics_str = match.group(1).strip()
                modifications["topics"] = [t.strip() for t in topics_str.split("、")]
        
        if modifications:
            self.record.confirm_record(pending["record_id"], modifications)
            return AgentResponse(
                success=True,
                message=f"已修改：{modifications}\n请确认或继续修改。",
                needs_confirmation=True,
            )
        
        return AgentResponse(
            success=False,
            message="请明确指出要修改的内容，例如：'修改内容：xxx' 或 '修改主题：工作'",
            needs_confirmation=True,
        )
    
    def get_command_suggestions(self) -> List[str]:
        return self.parser.get_command_suggestions()
