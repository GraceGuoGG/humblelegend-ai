"""指令解析Agent"""

import re


class CommandAgent:
    """指令解析Agent"""
    
    def __init__(self):
        """初始化"""
        self.commands = {
            "记录": self._parse_record,
            "帮我记录": self._parse_record,
            "记一下": self._parse_record,
            "热量": self._parse_calorie,
            "卡路里": self._parse_calorie,
            "吃了": self._parse_calorie,
            "收藏": self._parse_collection,
            "帮我收藏": self._parse_collection,
            "润色": self._parse_polish,
            "帮我润色": self._parse_polish,
            "日报": self._parse_daily_report,
            "今日日报": self._parse_daily_report,
            "给我日报": self._parse_daily_report,
            "复盘": self._parse_review,
            "给我复盘": self._parse_review,
            "主题复盘": self._parse_review,
            "设置": self._parse_setting,
            "帮我设置": self._parse_setting,
            "查看设置": self._parse_setting
        }
    
    def parse_command(self, text: str) -> dict:
        """解析指令"""
        for command, parser in self.commands.items():
            if command in text:
                return parser(text, command)
        
        # 默认为日常记录
        return {
            "type": "record",
            "subtype": "daily",
            "content": text,
            "theme": "工作"
        }
    
    def _parse_record(self, text: str, command: str) -> dict:
        """解析记录指令"""
        content = text.replace(command, "").strip()
        
        # 提取主题
        theme_pattern = r"主题([1-4]|作息|饮食|工作|娱乐)"
        theme_match = re.search(theme_pattern, content)
        theme = theme_match.group(1) if theme_match else "工作"
        
        # 移除主题信息
        if theme_match:
            content = content.replace(theme_match.group(0), "").strip()
        
        return {
            "type": "record",
            "subtype": "daily",
            "content": content,
            "theme": theme
        }
    
    def _parse_calorie(self, text: str, command: str) -> dict:
        """解析热量估算指令"""
        content = text.replace(command, "").strip()
        return {
            "type": "record",
            "subtype": "calorie",
            "content": content
        }
    
    def _parse_collection(self, text: str, command: str) -> dict:
        """解析收藏指令"""
        content = text.replace(command, "").strip()
        return {
            "type": "record",
            "subtype": "collection",
            "content": content
        }
    
    def _parse_polish(self, text: str, command: str) -> dict:
        """解析润色指令"""
        content = text.replace(command, "").strip()
        
        # 提取风格
        style_pattern = r"风格(正式|友好|default)"
        style_match = re.search(style_pattern, content)
        style = style_match.group(1) if style_match else "default"
        
        # 移除风格信息
        if style_match:
            content = content.replace(style_match.group(0), "").strip()
        
        return {
            "type": "record",
            "subtype": "polish",
            "content": content,
            "style": style
        }
    
    def _parse_daily_report(self, text: str, command: str) -> dict:
        """解析日报指令"""
        return {
            "type": "report",
            "subtype": "daily"
        }
    
    def _parse_review(self, text: str, command: str) -> dict:
        """解析复盘指令"""
        # 提取主题
        theme_pattern = r"主题([1-4]|作息|饮食|工作|娱乐)"
        theme_match = re.search(theme_pattern, text)
        theme = theme_match.group(1) if theme_match else "整体"
        
        return {
            "type": "report",
            "subtype": "review",
            "theme": theme
        }
    
    def _parse_setting(self, text: str, command: str) -> dict:
        """解析设置指令"""
        content = text.replace(command, "").strip()
        
        if "主题" in content:
            return {
                "type": "setting",
                "setting_type": "主题",
                "value": content
            }
        elif "目标" in content:
            return {
                "type": "setting",
                "setting_type": "目标",
                "value": content
            }
        elif "数据留存" in content:
            return {
                "type": "setting",
                "setting_type": "数据留存",
                "value": content
            }
        else:
            return {
                "type": "setting",
                "setting_type": "查看设置",
                "value": ""
            }