"""CLI接口（简化版）"""

import json
from src.core.simple_app import SimpleHumbleLegendApp


def run_cli(input_text=None, json_input=None):
    """运行CLI接口"""
    app = SimpleHumbleLegendApp()
    
    try:
        if json_input:
            # JSON模式
            data = json.loads(json_input)
            user_id = data.get("user_id", "default_user")
            input_text = data.get("input", "")
            result = app.process(user_id, input_text)
            print(json.dumps({"result": result}))
        else:
            # 交互模式
            if input_text:
                # 单条指令模式
                result = app.process("default_user", input_text)
                print(result)
            else:
                # 交互式模式
                print("HumbleLegend AI Agent")
                print("输入指令，按Ctrl+C退出")
                print("可用指令：")
                print("- 记录/帮我记录 [内容] [主题1-4或作息/饮食/工作/娱乐]")
                print("- 热量/卡路里/吃了 [食物]")
                print("- 收藏/帮我收藏 [内容或URL]")
                print("- 润色/帮我润色 [文本] [风格正式/友好]")
                print("- 日报/今日日报/给我日报")
                print("- 复盘/给我复盘/主题复盘 [主题1-4或作息/饮食/工作/娱乐]")
                
                while True:
                    try:
                        user_input = input("\n请输入指令：")
                        if not user_input:
                            continue
                        result = app.process("default_user", user_input)
                        print("\n" + result)
                    except KeyboardInterrupt:
                        print("\n退出程序")
                        break
    finally:
        pass