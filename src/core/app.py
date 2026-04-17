"""主应用类 - 简化版"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../..')

import re
import json
from datetime import datetime, timedelta

from src.core.database import init_db, get_or_create_user
from src.core.db_utils import (
    add_record, add_calorie_record, add_collection, add_polish_record,
    get_records_by_date, get_calorie_records_by_date,
    get_collections_by_date, get_polish_records_by_date,
    get_all_records, get_all_calorie_records,
    get_all_collections, get_all_polish_records,
    get_records_by_theme,
    get_user_settings, update_user_settings,
    add_command_memory
)


# 主题映射
THEME_MAP = {
    '1': 1, '2': 2, '3': 3, '4': 4,
    '作息': 1, '饮食': 2, '工作': 3, '娱乐': 4
}

THEME_NAMES = ['', '作息', '饮食', '工作', '娱乐']


class HumbleLegendApp:
    """主应用类"""
    
    def __init__(self):
        """初始化"""
        # 初始化数据库
        init_db()
        
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
        # 获取或创建用户
        get_or_create_user(user_id)
        
        # 添加命令记忆
        command_type = self._classify_command(input_text)
        add_command_memory(user_id, command_type, input_text)
        
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
        text = text.lower().strip()
        
        if '记录' in text or '帮我记录' in text:
            return 'record'
        elif '热量' in text or '卡路里' in text or '吃了' in text:
            return 'calorie'
        elif '收藏' in text or '帮我收藏' in text:
            return 'collect'
        elif '润色' in text or '帮我润色' in text:
            return 'polish'
        elif '日报' in text or '今日日报' in text or '给我日报' in text:
            return 'daily_report'
        elif '复盘' in text or '给我复盘' in text or '主题复盘' in text:
            return 'review'
        elif '设置' in text or '查看设置' in text:
            return 'settings'
        
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
        
        add_record(user_id, content, theme)
        
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
            add_calorie_record(user_id, food, calorie)
        
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
        add_collection(user_id, title, content)
        
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
        add_polish_record(user_id, original_text, polished_text, style)
        
        current_time = datetime.now().strftime('%H:%M')
        return f"{current_time}，已润色（{style}）：\n{polished_text}"
    
    def _handle_daily_report(self, user_id):
        """生成日报"""
        today = datetime.now()
        
        records = get_records_by_date(user_id, today)
        calorie_records = get_calorie_records_by_date(user_id, today)
        collections = get_collections_by_date(user_id, today)
        polish_records = get_polish_records_by_date(user_id, today)
        
        report = []
        report.append(f"# 今日日报 ({today.strftime('%Y-%m-%d')})")
        report.append("")
        
        # 数据卡片
        report.append("## 📊 数据卡片")
        report.append("- **今日记录数**: " + str(len(records)))
        report.append("- **热量摄入**: " + str(sum(r['calorie'] for r in calorie_records)) + " 千卡")
        report.append("- **收藏内容**: " + str(len(collections)) + " 条")
        report.append("- **润色文本**: " + str(len(polish_records)) + " 条")
        report.append("")
        
        # 当日总结
        report.append("## 📝 当日总结")
        summary = self._generate_summary(records, calorie_records, collections, polish_records)
        report.append(summary)
        report.append("")
        
        # 主题box
        report.append("## 📦 主题box")
        for theme in range(1, 5):
            theme_records = [r for r in records if r['theme'] == theme]
            if theme_records:
                report.append(f"### {THEME_NAMES[theme]}")
                for record in theme_records:
                    report.append(f"- {record['content']}")
                report.append("")
        
        return '\n'.join(report)
    
    def _handle_review(self, user_id, text):
        """生成复盘报告"""
        # 提取主题
        theme = None
        for key, value in THEME_MAP.items():
            if key in text:
                theme = value
                break
        
        today = datetime.now()
        seven_days_ago = today - timedelta(days=7)
        eight_weeks_ago = today - timedelta(weeks=8)
        
        if theme:
            records = get_records_by_theme(user_id, theme, days=56)
            calorie_records = get_all_calorie_records(user_id, days=56)
            collections = get_all_collections(user_id, days=56)
            polish_records = get_all_polish_records(user_id, days=56)
        else:
            records = get_all_records(user_id, days=56)
            calorie_records = get_all_calorie_records(user_id, days=56)
            collections = get_all_collections(user_id, days=56)
            polish_records = get_all_polish_records(user_id, days=56)
        
        report = []
        report.append(f"# 复盘报告 - {THEME_NAMES[theme] if theme else '整体情况'}")
        report.append("")
        
        report.append("## 📈 历史数据趋势")
        report.append("### 近7天趋势")
        seven_day_trend = self._generate_seven_day_trend(records, calorie_records, today)
        report.append(seven_day_trend)
        report.append("")
        
        report.append("### 近8周趋势")
        eight_week_trend = self._generate_eight_week_trend(records, calorie_records, today)
        report.append(eight_week_trend)
        report.append("")
        
        report.append("## 📝 主题总结")
        summary = self._generate_summary(records, calorie_records, collections, polish_records)
        report.append(summary)
        report.append("")
        
        report.append("## 📦 主题box")
        if theme:
            theme_records = [r for r in records if r['theme'] == theme]
            theme_records.sort(key=lambda x: x['created_at'])
            for record in theme_records:
                report.append(f"- {record['created_at']}: {record['content']}")
        else:
            for t in range(1, 5):
                theme_records = [r for r in records if r['theme'] == t]
                if theme_records:
                    report.append(f"### {THEME_NAMES[t]}")
                    theme_records.sort(key=lambda x: x['created_at'])
                    for record in theme_records:
                        report.append(f"- {record['created_at']}: {record['content']}")
                    report.append("")
        
        return '\n'.join(report)
    
    def _handle_settings(self, user_id, text):
        """处理设置命令"""
        settings = get_user_settings(user_id)
        
        if '查看设置' in text:
            theme_settings = json.loads(settings['theme_settings'])
            daily_target = settings['daily_record_target']
            
            report = []
            report.append("## ⚙️ 当前设置")
            report.append("- **主题设置**: " + ', '.join(theme_settings))
            report.append("- **每日记录目标**: " + str(daily_target) + " 条")
            report.append("- **数据留存**: 永久留存")
            return '\n'.join(report)
        
        # 简单的设置处理
        if '主题' in text:
            # 更新主题设置
            new_themes = []
            for key in THEME_MAP:
                if key in text and len(key) > 1:  # 只匹配中文主题
                    new_themes.append(key)
            if new_themes:
                update_user_settings(user_id, theme_settings=new_themes)
                return "主题设置已更新: " + ', '.join(new_themes)
        
        if '目标' in text:
            # 更新每日记录目标
            match = re.search(r'(\d+)条', text)
            if match:
                target = int(match.group(1))
                update_user_settings(user_id, daily_record_target=target)
                return f"每日记录目标已更新: {target}条"
        
        return "设置命令格式不正确，请使用：\n- 查看设置\n- 设置 主题 [主题1,主题2,...]\n- 设置 目标 [数字]条"
    
    def _handle_unknown(self):
        """处理未知命令"""
        help_text = """
我还不能理解您的请求。请使用以下格式：

📝 记录类：
- 记录 [内容] [主题]
- 帮我记录 [内容] [主题]

🔥 热量类：
- 热量 [食物]
- 卡路里 [食物]
- 吃了 [食物]

📚 收藏类：
- 收藏 [内容或URL]
- 帮我收藏 [内容或URL]

✨ 润色类：
- 润色 [文本] [风格正式/友好]
- 帮我润色 [文本] [风格正式/友好]

📊 日报类：
- 日报
- 今日日报
- 给我日报

📈 复盘类：
- 复盘 [主题1-4或作息/饮食/工作/娱乐]
- 给我复盘 [主题1-4或作息/饮食/工作/娱乐]
- 主题复盘 [主题1-4或作息/饮食/工作/娱乐]

⚙️ 设置类：
- 查看设置
- 设置 主题 [主题1,主题2,...]
- 设置 目标 [数字]条
        """.strip()
        
        return help_text
    
    def _generate_summary(self, records, calorie_records, collections, polish_records):
        """生成总结"""
        parts = []
        
        if records:
            parts.append(f"今日共记录了{len(records)}条内容，")
        
        if calorie_records:
            total_calories = sum(r['calorie'] for r in calorie_records)
            parts.append(f"摄入热量{total_calories:.0f}千卡，")
            if total_calories > 2000:
                parts.append("超过了每日推荐摄入量。")
            else:
                parts.append("在合理范围内。")
        
        if collections:
            parts.append(f"收藏了{len(collections)}条内容，")
        
        if polish_records:
            parts.append(f"润色了{len(polish_records)}条文本，")
        
        if not parts:
            return "今日暂无记录，建议开始记录生活和工作。"
        
        return ''.join(parts).rstrip('，') + '。'
    
    def _generate_seven_day_trend(self, records, calorie_records, today):
        """生成近7天趋势"""
        trend = []
        for i in range(7):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            day_records = [r for r in records if date_str in r['created_at']]
            record_count = len(day_records)
            
            day_calories = [r for r in calorie_records if date_str in r['created_at']]
            calorie_total = sum(r['calorie'] for r in day_calories)
            
            trend.append(f"- {date_str}: 记录{record_count}条，热量{calorie_total:.0f}千卡")
        
        return '\n'.join(trend)
    
    def _generate_eight_week_trend(self, records, calorie_records, today):
        """生成近8周趋势"""
        trend = []
        for i in range(8):
            week_start = today - timedelta(weeks=i, days=today.weekday())
            week_end = week_start + timedelta(days=6)
            week_str = f"{week_start.strftime('%Y-%m-%d')} 至 {week_end.strftime('%Y-%m-%d')}"
            
            week_records = []
            week_calories = []
            
            for record in records:
                record_date = datetime.strptime(record['created_at'][:10], '%Y-%m-%d').date()
                if week_start.date() <= record_date <= week_end.date():
                    week_records.append(record)
            
            for record in calorie_records:
                record_date = datetime.strptime(record['created_at'][:10], '%Y-%m-%d').date()
                if week_start.date() <= record_date <= week_end.date():
                    week_calories.append(record)
            
            record_count = len(week_records)
            calorie_total = sum(r['calorie'] for r in week_calories)
            
            trend.append(f"- {week_str}: 记录{record_count}条，热量{calorie_total:.0f}千卡")
        
        return '\n'.join(trend)


def main():
    """主函数"""
    print("HumbleLegend AI Agent 已启动")
    print("输入 'help' 查看帮助，'exit' 退出")
    
    # 初始化数据库
    init_db()
    
    # 创建应用实例
    app = HumbleLegendApp()
    
    while True:
        user_input = input("用户: ").strip()
        
        if user_input.lower() == 'exit':
            print("再见！")
            break
        
        if user_input.lower() == 'help':
            print(app._handle_unknown())
            continue
        
        result = app.process('default_user', user_input)
        print("AI: ", result)


if __name__ == "__main__":
    main()