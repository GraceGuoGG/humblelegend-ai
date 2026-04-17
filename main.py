#!/usr/bin/env python3
"""HumbleLegend AI Agent 主入口（最终简化版）"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from src.core.simple_app import SimpleHumbleLegendApp
from src.platforms.cli import run_cli

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="HumbleLegend AI Agent")
    parser.add_argument("--mode", choices=["cli", "api"], default="cli", help="运行模式")
    parser.add_argument("--input", type=str, help="输入内容")
    parser.add_argument("--json", type=str, help="JSON格式输入")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="API服务主机")
    parser.add_argument("--port", type=int, default=8000, help="API服务端口")
    
    args = parser.parse_args()
    
    if args.mode == "cli":
        run_cli(args.input, args.json)
    elif args.mode == "api":
        from src.api.simple_server import start_server
        start_server(args.host, args.port)

if __name__ == "__main__":
    main()
