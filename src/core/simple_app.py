"""简单的应用版本，不使用SQLite"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../..')

import re
import json
from datetime import datetime, timedelta

from src.core.simple_database import SimpleDatabase


# 主题映射
THEME_MAP = {
    '1': 1, '2': 2, '3': 3, '4': 4,
    '作息': 1, '饮食': 2, '工作': 3, '娱乐': 4
}

THEME_NAMES = ['', '作息', '饮食', '工作', '娱乐']


class SimpleHumbleLegendApp:
    """简单的HumbleLegend应用"""
    
    def __init__(self):
        """初始化"""
        self.db = SimpleDatabase()
        
        # 食品热量数据库（简化版）
        self.food_calories = {
            '米饭': 130, '馒头': 221, '面条': 109,
            '苹果': 52, '香蕉': 89, '橙子': 47,
            '鸡蛋': 155, '牛奶': 54, '鸡肉': 165,
            '猪肉': 395, '牛肉': 125, '鱼肉': 124,
            '德芙巧克力': 544, '薯片': 548, '饼干': 433,
            '鱼香肉丝': 150, '宫保鸡丁': 194, '麻婆豆腐': 145
        }
    
    def process(self, user_id, input_text):
        """处理用户输入"""
        # 添加命令记忆
        command_type = self._classify_command(input_text)
        self.db.add_command_memory(user_id, command_type, input_text)
        
        # 处理命令
        if command_type == 'record':
            return self._handle_record(user_id, input_text)
        elif command_type == 'calorie':
            return self._handle_calorie(user_id, input_text)
        elif command_type == 'collect':
            return self._handle_collect(user_id, input_text)
        elif command_type == 'polish':
            return self._handle_polish(user_id, input_text)
        elif command_type == 'daily_report':
            return self._handle_daily_report(user_id)
        elif command_type == 'review':
            return self._handle_review(user_id, input_text)
        elif command_type == 'settings':
            return self._handle_settings(user_id, input_text)
        else:
            return self._handle_unknown()
    
    def _classify_command(self, text):
        """分类用户命令"""
        print(f"分类命令前的原始文本: '{text}'")
        text = text.lower().strip()
        print(f"处理后的文本: '{text}'")
        
        if '记录' in text or '帮我记录' in text:
            print("分类为: record")
            return 'record'
        elif '热量' in text or '卡路里' in text or '吃了' in text:
            print("分类为: calorie")
            return 'calorie'
        elif '收藏' in text or '帮我收藏' in text:
            print("分类为: collect")
            return 'collect'
        elif '润色' in text or '帮我润色' in text:
            print("分类为: polish")
            return 'polish'
        elif '日报' in text or '今日日报' in text or '给我日报' in text:
            print("分类为: daily_report")
            return 'daily_report'
        elif '复盘' in text or '给我复盘' in text or '主题复盘' in text:
            print("分类为: review")
            return 'review'
        elif '设置' in text or '查看设置' in text:
            print("分类为: settings")
            return 'settings'
        
        print("分类为: unknown")
        return 'unknown'
    
    def _handle_record(self, user_id, text):
        """处理记录命令"""
        # 提取内容和主题
        content = re.sub(r'帮我记录|记录', '', text).strip()
        theme = 3  # 默认工作主题
        
        # 提取主题
        for key, value in THEME_MAP.items():
            if key in content:
                theme = value
                content = re.sub(key, '', content).strip()
        
        self.db.add_record(user_id, content, theme)
        
        # 获取当前时间
        current_time = datetime.now().strftime('%H:%M')
        
        return f"{current_time}，已记录：{content}（{THEME_NAMES[theme]}）"
    
    def _handle_calorie(self, user_id, text):
        """处理热量计算命令"""
        # 提取食物信息
        food_text = re.sub(r'热量|卡路里|吃了', '', text).strip()
        
        # 分割食物
        foods = re.split(r'[,，]', food_text)
        foods = [f.strip() for f in foods if f.strip()]
        
        total_calories = 0
        details = []
        
        for food in foods:
            # 计算单种食物的热量
            calorie = 0
            
            # 检查是否包含数量
            match = re.search(r'(\d+(\.\d+)?)([个只斤克g]?)', food)
            if match:
                quantity = float(match.group(1))
                unit = match.group(3)
                food_name = re.sub(r'\d+(\.\d+)?[个只斤克g]?', '', food).strip()
                # 计算热量
                if food_name in self.food_calories:
                    base_calorie = self.food_calories[food_name]
                    # 简单计算（默认每100g）
                    if unit in ['克', 'g']:
                        calorie = base_calorie * (quantity / 100)
                    elif unit in ['斤']:
                        calorie = base_calorie * (quantity * 500 / 100)
                    elif unit in ['个', '只'] or not unit:
                        # 默认每个按100g计算
                        calorie = base_calorie
                details.append(f"{food}: {calorie:.1f}千卡")
                total_calories += calorie
            else:
                # 无数量，默认按100g计算
                if food in self.food_calories:
                    calorie = self.food_calories[food]
                    details.append(f"{food}: {calorie}千卡")
                    total_calories += calorie
        
        # 保存到数据库
        for food in foods:
            self.db.add_calorie_record(user_id, food, calorie)
        
        # 生成回复
        current_time = datetime.now().strftime('%H:%M')
        reply = f"{current_time}，"
        if details:
            reply += f"热量计算完成：\n" + '\n'.join(details)
            reply += f"\n总计：{total_calories:.1f}千卡"
        else:
            reply += "未找到对应的食物信息，无法计算热量。"
        
        return reply
    
    def _handle_collect(self, user_id, text):
        """处理收藏命令"""
        content = re.sub(r'收藏|帮我收藏', '', text).strip()
        
        title = content[:50] if len(content) > 50 else content
        self.db.add_collection(user_id, title, content)
        
        current_time = datetime.now().strftime('%H:%M')
        return f"{current_time}，已收藏：{title}"
    
    def _handle_polish(self, user_id, text):
        """处理润色命令"""
        original_text = text
        polished_text = original_text
        
        # 简单的润色逻辑
        if '正式' in text:
            polished_text = original_text.replace('你好', '您好').replace('谢谢', '感谢')
        elif '友好' in text:
            polished_text = original_text.replace('您好', '你好').replace('感谢', '谢谢')
        
        # 提取原始文本
        match = re.search(r'润色\s*(.*?)\s*(正式|友好)', text)
        if match:
            original_text = match.group(1).strip()
        
        style = '正式' if '正式' in text else '友好'
        self.db.add_polish_record(user_id, original_text, polished_text, style)
        
        current_time = datetime.now().strftime('%H:%M')
        return f"{current_time}，已润色（{style}）：\n{polished_text}"
    
    def _handle_daily_report(self, user_id):
        """生成日报"""
        today = datetime.now()
        
        records = self.db.get_records_by_date(user_id, today)
        calorie_records = self.db.get_calorie_records_by_date(user_id, today)
        collections = self.db.get_collections_by_date(user_id, today)
        polish_records = self.db.get_polish_records_by_date(user_id, today)
        
        try:
            reply = f"今日日报 ({today.strftime('%Y年%m月%d日')})\n\n"
        except Exception as e:
            print(f"日期格式化错误: {e}")
            reply = f"今日日报 ({today.strftime('%Y-%m-%d')})\n\n"
        
        if records:
            reply += "记录：\n"
            for record in records:
                reply += f"- {record['content']} ({THEME_NAMES[record['theme']]})\n"
        
        if calorie_records:
            reply += "\n饮食：\n"
            for record in calorie_records:
                reply += f"- {record['food']}: {record['calories']}千卡\n"
        
        if collections:
            reply += "\n收藏：\n"
            for collection in collections:
                reply += f"- {collection['title']}\n"
        
        if polish_records:
            reply += "\n润色：\n"
            for record in polish_records:
                reply += f"- [{record['style']}]: {record['original_text']} → {record['polished_text']}\n"
        
        return reply
    
    def _handle_review(self, user_id, text):
        """处理复盘命令"""
        today = datetime.now()
        
        records = self.db.get_records_by_date(user_id, today)
        reply = f"今日复盘 ({today.strftime('%Y年%m月%d日')})\n\n"
        
        if records:
            reply += "记录：\n"
            for record in records:
                reply += f"- {record['content']} ({THEME_NAMES[record['theme']]})\n"
        
        return reply
    
    def _handle_settings(self, user_id, text):
        """处理设置命令"""
        return "设置功能暂未实现，请使用默认设置"
    
    def _handle_unknown(self):
        """处理未知命令"""
        return "我还不能理解您的请求。请使用以下格式：\n\n记录类：\n- 记录 [内容] [主题]\n- 帮我记录 [内容] [主题]\n\n热量类：\n- 热量 [食物]\n- 卡路里 [食物]\n- 吃了 [食物]\n\n收藏类：\n- 收藏 [内容或URL]\n- 帮我收藏 [内容或URL]\n\n润色类：\n- 润色 [文本] [风格正式/友好]\n- 帮我润色 [文本] [风格正式/友好]\n\n日报类：\n- 日报\n- 今日日报\n- 给我日报\n\n复盘类：\n- 复盘 [主题1-4或作息/饮食/工作/娱乐]\n- 给我复盘 [主题1-4或作息/饮食/工作/娱乐]\n- 主题复盘 [主题1-4或作息/饮食/工作/娱乐]\n\n设置类：\n- 查看设置\n- 设置 主题 [主题1,主题2,...]\n- 设置 目标 [数字]条"