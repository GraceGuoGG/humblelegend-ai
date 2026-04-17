"""
HumbleLegend AI Agent
轻量级AI助手，用于零散信息存档、收集、分析与汇总
"""

__version__ = "1.0.0"
__author__ = "HumbleLegend Team"

from .agents.orchestrator import OrchestratorAgent
from .core.config import Config, load_config

__all__ = [
    "OrchestratorAgent",
    "Config",
    "load_config",
]
