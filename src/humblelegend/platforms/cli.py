"""
CLI平台适配
命令行交互入口
"""

import argparse
import json
import sys
from typing import Any, Dict, Optional

from ..agents.orchestrator import OrchestratorAgent
from ..core.config import load_config
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')


class CLIPlatform:
    def __init__(self, config_path: Optional[str] = None):
        self.config = load_config(config_path)
        self.orchestrator = OrchestratorAgent(self.config)
    
    def run_interactive(self, user_id: str = "default_user") -> None:
        print("=" * 50)
        print("  HumbleLegend AI Agent - CLI模式")
        print("=" * 50)
        print("\n可用指令：")
        for suggestion in self.orchestrator.get_command_suggestions():
            print(f"  - {suggestion}")
        print("\n输入 'exit' 或 'quit' 退出")
        print("-" * 50 + "\n")
        
        while True:
            try:
                user_input = input("您: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["exit", "quit", "退出"]:
                    print("\n再见！")
                    break
                
                response = self.orchestrator.process(user_input, user_id)
                
                print(f"\nAgent: {response.message}\n")
                
            except KeyboardInterrupt:
                print("\n\n再见！")
                break
            except Exception as e:
                logger.error(f"处理异常: {e}")
                print(f"\n[错误] {str(e)}\n")
    
    def run_single(self, user_input: str, user_id: str = "default_user") -> Dict[str, Any]:
        response = self.orchestrator.process(user_input, user_id)
        return response.to_dict()
    
    def run_json(self, json_input: str) -> str:
        try:
            data = json.loads(json_input)
            
            user_input = data.get("input", "")
            user_id = data.get("user_id", "default_user")
            attachments = data.get("attachments", [])
            
            response = self.orchestrator.process(user_input, user_id, attachments)
            
            return json.dumps(response.to_dict(), ensure_ascii=False, indent=2)
            
        except json.JSONDecodeError as e:
            return json.dumps({
                "success": False,
                "message": f"JSON解析错误: {str(e)}",
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "success": False,
                "message": f"处理错误: {str(e)}",
            }, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description="HumbleLegend AI Agent - 轻量级AI助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互模式
  python -m humblelegend

  # 单条指令
  python -m humblelegend --input "帮我记录今天完成了项目汇报"

  # JSON模式
  python -m humblelegend --json '{"input": "给我今日日报", "user_id": "user123"}'
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="单条输入指令"
    )
    
    parser.add_argument(
        "--json", "-j",
        type=str,
        help="JSON格式输入"
    )
    
    parser.add_argument(
        "--user-id", "-u",
        type=str,
        default="default_user",
        help="用户ID (默认: default_user)"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="配置文件路径"
    )
    
    parser.add_argument(
        "--api",
        action="store_true",
        help="启动HTTP API服务"
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8000,
        help="API服务端口 (默认: 8000)"
    )
    
    args = parser.parse_args()
    
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")
    
    if args.api:
        try:
            from ..api.routes import run_api
            run_api(port=args.port)
            return
        except ImportError as e:
            logger.error(f"API模式需要fastapi和uvicorn依赖: {e}")
            logger.info("使用CLI模式运行")
    
    cli = CLIPlatform(args.config)
    
    if args.json:
        result = cli.run_json(args.json)
        print(result)
    
    elif args.input:
        result = cli.run_single(args.input, args.user_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        cli.run_interactive(args.user_id)


if __name__ == "__main__":
    main()
