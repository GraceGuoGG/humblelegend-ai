#!/usr/bin/env python3
"""
简化版HumbleLegend AI Agent
不依赖外部库，使用内存存储
"""

import logging
import argparse
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

class IntentType:
    RECORD_DAILY = "record_daily"
    RECORD_CALORIE = "record_calorie"
    COLLECT = "collect"
    POLISH = "polish"
    DAILY_REPORT_TODAY = "daily_report_today"
    DAILY_REPORT_HISTORY = "daily_report_history"
    REVIEW = "review"
    SETTINGS = "settings"
    MEMORY_CLEAR = "memory_clear"
    MEMORY_QUERY = "memory_query"
    UNKNOWN = "unknown"

class ParsedCommand:
    def __init__(self, intent, content="", params=None, attachments=None, raw_input=""):
        self.intent = intent
        self.content = content
        self.params = params or {}
        self.attachments = attachments or []
        self.raw_input = raw_input
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class ParserAgent:
    COMMAND_PATTERNS = {
        IntentType.RECORD_DAILY: [
            "帮我记录日常", "记录日常", "记日常", "帮我记一下", "记录一下"
        ],
        IntentType.RECORD_CALORIE: [
            "帮我估算热量", "估算热量", "计算热量", "帮我算热量"
        ],
        IntentType.COLLECT: [
            "帮我收藏", "收藏", "保存", "帮我保存"
        ],
        IntentType.POLISH: [
            "帮我润色", "润色", "修改", "帮我修改"
        ],
        IntentType.DAILY_REPORT_TODAY: [
            "给我今日日报", "今日日报", "日报", "今天的日报"
        ],
        IntentType.DAILY_REPORT_HISTORY: [
            "给我日报", "历史日报", "查看日报"
        ],
        IntentType.REVIEW: [
            "复盘", "帮我复盘", "总结", "帮我总结"
        ],
        IntentType.SETTINGS: [
            "设置", "配置", "修改设置", "更改配置"
        ],
        IntentType.MEMORY_CLEAR: [
            "清除记忆", "删除记忆", "清空记忆"
        ],
        IntentType.MEMORY_QUERY: [
            "查看记忆", "查询记忆", "记忆"
        ]
    }

    def parse(self, user_input: str, attachments: Optional[List[Dict[str, Any]]] = None) -> ParsedCommand:
        user_input = user_input.strip()
        
        # 处理纯图片/视频输入
        if not user_input and attachments:
            return ParsedCommand(
                intent=IntentType.RECORD_DAILY,
                content="[多媒体材料]",
                raw_input=user_input,
                attachments=attachments
            )
        
        for intent, patterns in self.COMMAND_PATTERNS.items():
            for pattern in patterns:
                if pattern in user_input:
                    content = user_input.replace(pattern, "").strip()
                    return ParsedCommand(
                        intent=intent,
                        content=content,
                        raw_input=user_input,
                        attachments=attachments
                    )
        
        return ParsedCommand(
            intent=IntentType.UNKNOWN,
            content=user_input,
            raw_input=user_input,
            attachments=attachments
        )

class MemoryStorage:
    def __init__(self):
        self.memories = {
            "records": [],
            "calorie_records": [],
            "collections": [],
            "polished_texts": []
        }

    def add_record(self, user_id, content, record_type):
        record = {
            "id": len(self.memories["records"]) + 1,
            "user_id": user_id,
            "content": content,
            "record_type": record_type,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.memories["records"].append(record)
        return record

    def add_calorie_record(self, user_id, food, calories):
        record = {
            "id": len(self.memories["calorie_records"]) + 1,
            "user_id": user_id,
            "food": food,
            "calories": calories,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.memories["calorie_records"].append(record)
        return record

    def add_collection(self, user_id, content, url=None):
        record = {
            "id": len(self.memories["collections"]) + 1,
            "user_id": user_id,
            "content": content,
            "url": url,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.memories["collections"].append(record)
        return record

    def add_polished_text(self, user_id, original, polished):
        record = {
            "id": len(self.memories["polished_texts"]) + 1,
            "user_id": user_id,
            "original": original,
            "polished": polished,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.memories["polished_texts"].append(record)
        return record

    def get_records(self, user_id, date=None):
        if date:
            return [r for r in self.memories["records"] if r["user_id"] == user_id and r["created_at"].startswith(date)]
        return [r for r in self.memories["records"] if r["user_id"] == user_id]

    def get_calorie_records(self, user_id, date=None):
        if date:
            return [r for r in self.memories["calorie_records"] if r["user_id"] == user_id and r["created_at"].startswith(date)]
        return [r for r in self.memories["calorie_records"] if r["user_id"] == user_id]
    
    def get_collections(self, user_id, date=None):
        if date:
            return [r for r in self.memories["collections"] if r["user_id"] == user_id and r["created_at"].startswith(date)]
        return [r for r in self.memories["collections"] if r["user_id"] == user_id]

class OrchestratorAgent:
    def __init__(self):
        self.parser = ParserAgent()
        self.memory = MemoryStorage()

    def process(self, user_input, user_id="default_user", attachments=None):
        parsed = self.parser.parse(user_input, attachments)
        
        if parsed.intent == IntentType.RECORD_DAILY:
            return self._handle_record_daily(parsed, user_id)
        elif parsed.intent == IntentType.RECORD_CALORIE:
            return self._handle_record_calorie(parsed, user_id)
        elif parsed.intent == IntentType.COLLECT:
            return self._handle_collect(parsed, user_id)
        elif parsed.intent == IntentType.POLISH:
            return self._handle_polish(parsed, user_id)
        elif parsed.intent == IntentType.DAILY_REPORT_TODAY:
            return self._handle_daily_report_today(user_id)
        elif parsed.intent == IntentType.REVIEW:
            return self._handle_review(parsed, user_id)
        else:
            return {
                "success": True,
                "message": "我没有理解您的指令，请尝试使用以下指令：\n- 帮我记录日常...\n- 帮我估算热量...\n- 帮我收藏...\n- 帮我润色...\n- 给我今日日报\n- 复盘...",
                "data": None
            }

    def _handle_record_daily(self, parsed, user_id):
        if not parsed.content:
            return {
                "success": False,
                "message": "请告诉我要记录的内容",
                "data": None
            }
        
        record = self.memory.add_record(user_id, parsed.content, "daily")
        timestamp = datetime.now().strftime("%H:%M")
        return {
            "success": True,
            "message": f"{timestamp}，{parsed.content}",
            "data": record
        }

    def _handle_record_calorie(self, parsed, user_id):
        if not parsed.content:
            return {
                "success": False,
                "message": "请告诉我要估算热量的食物",
                "data": None
            }
        
        # 简单的热量估算
        calories = self._estimate_calories(parsed.content)
        record = self.memory.add_calorie_record(user_id, parsed.content, calories)
        return {
            "success": True,
            "message": f"{parsed.content} 的热量约为 {calories} 千卡",
            "data": record
        }

    def _estimate_calories(self, food):
        # 扩展的热量估算逻辑，支持多种食材、零食和菜品
        food_calories = {
            # 基础食材
            "米饭": 116,
            "面条": 137,
            "面包": 265,
            "鸡蛋": 155,
            "牛奶": 42,
            "苹果": 52,
            "香蕉": 89,
            "鸡肉": 165,
            "牛肉": 250,
            "鱼肉": 200,
            # 零食
            "巧克力": 546,
            "德芙巧克力": 546,
            "薯片": 540,
            "饼干": 430,
            "蛋糕": 347,
            "冰淇淋": 207,
            # 菜品
            "鱼香肉丝": 194,
            "宫保鸡丁": 175,
            "红烧肉": 470,
            "糖醋排骨": 350,
            "麻婆豆腐": 140,
            "炒青菜": 80,
            "西红柿炒蛋": 150
        }
        
        # 支持多种食材的热量计算
        total_calories = 0
        ingredients = food.split(" ")
        
        for ingredient in ingredients:
            for item, calories in food_calories.items():
                if item in ingredient:
                    total_calories += calories
                    break
        
        if total_calories > 0:
            return total_calories
        return 100  # 默认值

    def _handle_collect(self, parsed, user_id):
        if not parsed.content:
            return {
                "success": False,
                "message": "请告诉我要收藏的内容",
                "data": None
            }
        
        url = None
        if "http://" in parsed.content or "https://" in parsed.content:
            url = parsed.content
            content = "网页链接"
        else:
            content = parsed.content
        
        record = self.memory.add_collection(user_id, content, url)
        return {
            "success": True,
            "message": f"已收藏：{content}",
            "data": record
        }

    def _handle_polish(self, parsed, user_id):
        if not parsed.content:
            return {
                "success": False,
                "message": "请告诉我要润色的文本",
                "data": None
            }
        
        # 简单的文本润色
        polished = self._polish_text(parsed.content)
        record = self.memory.add_polished_text(user_id, parsed.content, polished)
        return {
            "success": True,
            "message": f"润色结果：\n{polished}",
            "data": record
        }

    def _polish_text(self, text):
        # 简单的文本润色逻辑
        replacements = {
            "很棒": "非常出色",
            "很好": "非常优秀",
            "不错": "相当不错",
            "我觉得": "我认为",
            "你好": "您好"
        }
        
        polished = text
        for old, new in replacements.items():
            polished = polished.replace(old, new)
        
        return polished

    def _handle_daily_report_today(self, user_id):
        today = datetime.now().strftime("%Y-%m-%d")
        records = self.memory.get_records(user_id, today)
        calorie_records = self.memory.get_calorie_records(user_id, today)
        collect_records = self.memory.get_collections(user_id, today)
        
        # 检查是否有足够内容生成日报
        total_records = len(records) + len(calorie_records) + len(collect_records)
        if total_records < 2:
            return {
                "success": False,
                "message": "今日内容较少，无法生成完整日报。请补充更多记录后再尝试。",
                "data": None
            }
        
        # 1. 数据卡片
        report = f"# 今日日报 ({today})\n\n"
        report += "## 📊 数据卡片\n\n"
        
        # 固定核心指标
        report += "### 固定核心指标\n"
        report += f"- **今日消息会话数**：{total_records}\n"
        report += f"- **今日记录总数**：{total_records}\n"
        report += f"- **日常记录数**：{len(records)}\n"
        report += f"- **热量估算次数**：{len(calorie_records)}\n"
        report += f"- **收藏数**：{len(collect_records)}\n"
        
        # 灵活扩展指标
        report += "\n### 灵活扩展指标\n"
        if calorie_records:
            total_calories = sum(r['calories'] for r in calorie_records)
            report += f"- **今日营养摄入汇总**：\n"
            report += f"  - 热量：{total_calories} 千卡\n"
            report += f"  - 蛋白质：约 {int(total_calories * 0.15 / 4)} 克\n"
            report += f"  - 脂肪：约 {int(total_calories * 0.25 / 9)} 克\n"
            report += f"  - 碳水化合物：约 {int(total_calories * 0.6 / 4)} 克\n"
        
        # 2. 当日总结（500-800字）
        report += "\n## 📝 当日总结\n\n"
        summary = "今天是充实的一天。"
        
        if records:
            work_records = [r for r in records if "工作" in r['content'] or "项目" in r['content']]
            study_records = [r for r in records if "学习" in r['content'] or "学习了" in r['content']]
            
            if work_records:
                summary += "在工作方面，"
                for i, record in enumerate(work_records):
                    if i > 0: summary += "此外，"
                    summary += record['content'] + "。"
            
            if study_records:
                summary += "在学习方面，"
                for i, record in enumerate(study_records):
                    if i > 0: summary += "同时，"
                    summary += record['content'] + "。"
        
        if calorie_records:
            total_calories = sum(r['calories'] for r in calorie_records)
            summary += f"今日热量摄入总量为 {total_calories} 千卡，"
            if total_calories < 1500:
                summary += "热量摄入偏低，建议适当增加营养摄入。"
            elif total_calories > 2500:
                summary += "热量摄入偏高，建议注意饮食平衡。"
            else:
                summary += "热量摄入适中，保持良好的饮食习惯。"
        
        if collect_records:
            summary += f"今日收藏了 {len(collect_records)} 条内容，"
            summary += "为知识积累和信息管理提供了有力支持。"
        
        # 补充字数到500字左右
        while len(summary) < 500:
            summary += " 今日的各项活动反映了您积极的生活态度和工作学习热情。通过记录日常、估算热量、收藏内容等方式，您正在建立一个更加有序和健康的生活方式。继续保持这种良好的习惯，将会对您的个人发展和健康管理产生积极的影响。"
        
        if len(summary) > 800:
            summary = summary[:800] + "..."
        
        report += summary + "\n"
        
        # 3. 主题box
        report += "\n## 📦 主题box\n\n"
        
        # 按主题分类
        themes = {
            "工作": [],
            "学习": [],
            "生活": [],
            "其他": []
        }
        
        # 分类记录
        for record in records:
            content = record['content']
            time = record['created_at']
            if "工作" in content or "项目" in content:
                themes["工作"].append((time, content))
            elif "学习" in content or "学习了" in content:
                themes["学习"].append((time, content))
            else:
                themes["生活"].append((time, content))
        
        # 分类热量记录
        for record in calorie_records:
            content = f"热量估算：{record['food']} ({record['calories']} 千卡)"
            time = record['created_at']
            themes["生活"].append((time, content))
        
        # 分类收藏记录
        for record in collect_records:
            content = f"收藏：{record['content']}"
            time = record['created_at']
            themes["其他"].append((time, content))
        
        # 输出主题box
        for theme, items in themes.items():
            if items:
                # 按时间戳排序
                sorted_items = sorted(items, key=lambda x: x[0])
                report += f"### {theme}\n"
                for time, content in sorted_items:
                    time_str = time.split(' ')[1]
                    report += f"- **{time_str}**: {content}\n"
                report += "\n"
        
        # 4. 交互逻辑
        report += "\n---\n\n"
        report += "## 💬 交互反馈\n"
        report += "日报已生成，您对这份日报满意吗？\n"
        report += "- 输入 '调整' 可以修改日报内容\n"
        report += "- 输入 '补充' 可以添加更多内容\n"
        report += "- 输入 '确认' 可以保存这份日报\n"
        
        return {
            "success": True,
            "message": report,
            "data": {
                "records": records,
                "calorie_records": calorie_records,
                "collect_records": collect_records,
                "summary": summary
            }
        }

    def _handle_review(self, parsed, user_id):
        topic = parsed.content or "整体"
        records = self.memory.get_records(user_id)
        calorie_records = self.memory.get_calorie_records(user_id)
        collect_records = self.memory.get_collections(user_id)
        
        # 1. 历史数据趋势
        review = f"# {topic} 复盘\n\n"
        review += "## 📈 历史数据趋势\n\n"
        
        # 按天展示近7天趋势
        review += "### 近7天趋势\n"
        from datetime import datetime, timedelta
        today = datetime.now()
        daily_trends = {}
        
        # 初始化近7天数据
        for i in range(7):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            daily_trends[date] = {
                "record_count": 0,
                "calorie_count": 0,
                "total_calories": 0
            }
        
        # 统计每日记录数
        for record in records:
            date = record['created_at'].split(' ')[0]
            if date in daily_trends:
                daily_trends[date]["record_count"] += 1
        
        # 统计每日热量记录
        for record in calorie_records:
            date = record['created_at'].split(' ')[0]
            if date in daily_trends:
                daily_trends[date]["calorie_count"] += 1
                daily_trends[date]["total_calories"] += record['calories']
        
        # 输出近7天趋势
        for date in sorted(daily_trends.keys(), reverse=True):
            trend = daily_trends[date]
            review += f"- **{date}**: 记录数={trend['record_count']}, 热量记录数={trend['calorie_count']}, 总热量={trend['total_calories']}千卡\n"
        
        # 按周展示近8周趋势
        review += "\n### 近8周趋势\n"
        weekly_trends = {}
        
        # 初始化近8周数据
        for i in range(8):
            week_start = (today - timedelta(days=i*7)).strftime("%Y-%m-%d")
            weekly_trends[week_start] = {
                "record_count": 0,
                "calorie_count": 0,
                "total_calories": 0
            }
        
        # 统计每周记录数
        for record in records:
            record_date = datetime.strptime(record['created_at'].split(' ')[0], "%Y-%m-%d")
            week_start = (record_date - timedelta(days=record_date.weekday())).strftime("%Y-%m-%d")
            if week_start in weekly_trends:
                weekly_trends[week_start]["record_count"] += 1
        
        # 统计每周热量记录
        for record in calorie_records:
            record_date = datetime.strptime(record['created_at'].split(' ')[0], "%Y-%m-%d")
            week_start = (record_date - timedelta(days=record_date.weekday())).strftime("%Y-%m-%d")
            if week_start in weekly_trends:
                weekly_trends[week_start]["calorie_count"] += 1
                weekly_trends[week_start]["total_calories"] += record['calories']
        
        # 输出近8周趋势
        for week_start in sorted(weekly_trends.keys(), reverse=True):
            trend = weekly_trends[week_start]
            review += f"- **第{list(weekly_trends.keys()).index(week_start)+1}周** ({week_start}): 记录数={trend['record_count']}, 热量记录数={trend['calorie_count']}, 总热量={trend['total_calories']}千卡\n"
        
        # 2. 主题总结（500-800字）
        review += "\n## 📝 主题总结\n\n"
        summary = f"{topic}主题的复盘分析。"
        
        # 分析记录数据
        if records:
            topic_records = [r for r in records if topic in r['content'] or "整体" == topic]
            if topic_records:
                summary += f"在{topic}方面，共记录了{len(topic_records)}条相关内容。"
                
                # 分析最近的记录
                recent_topic_records = topic_records[-3:]
                for i, record in enumerate(recent_topic_records):
                    if i > 0: summary += "此外，"
                    summary += record['content'] + "。"
            else:
                summary += f"暂无{topic}相关的记录。"
        
        # 分析热量数据
        if calorie_records:
            total_calories = sum(r['calories'] for r in calorie_records)
            avg_calories = total_calories / len(calorie_records)
            summary += f"热量摄入方面，共记录了{len(calorie_records)}次，总热量{total_calories}千卡，平均每次{avg_calories:.1f}千卡。"
            
            if total_calories < 5000:
                summary += "总体热量摄入偏低，建议适当增加营养摄入。"
            elif total_calories > 10000:
                summary += "总体热量摄入偏高，建议注意饮食平衡。"
            else:
                summary += "总体热量摄入适中，保持良好的饮食习惯。"
        
        # 分析收藏数据
        if collect_records:
            summary += f"收藏方面，共收藏了{len(collect_records)}条内容，为知识积累和信息管理提供了有力支持。"
        
        # 补充字数到500字左右
        while len(summary) < 500:
            summary += " 从历史数据趋势来看，您在{topic}方面的记录呈现出一定的规律性。通过持续的记录和分析，您可以更好地了解自己的行为模式和习惯，从而做出更合理的规划和调整。建议继续保持记录的习惯，关注数据的变化趋势，及时发现问题并采取相应的措施。"
        
        if len(summary) > 800:
            summary = summary[:800] + "..."
        
        review += summary + "\n"
        
        # 3. 主题box
        review += "\n## 📦 主题box\n\n"
        
        # 按时间戳排序的所有内容
        all_contents = []
        
        # 添加记录内容
        for record in records:
            if topic in record['content'] or "整体" == topic:
                all_contents.append((record['created_at'], "记录", record['content']))
        
        # 添加热量记录
        for record in calorie_records:
            content = f"热量估算：{record['food']} ({record['calories']} 千卡)"
            all_contents.append((record['created_at'], "热量", content))
        
        # 添加收藏内容
        for record in collect_records:
            content = f"收藏：{record['content']}"
            all_contents.append((record['created_at'], "收藏", content))
        
        # 按时间戳排序
        all_contents.sort(key=lambda x: x[0])
        
        # 输出主题box
        if all_contents:
            for timestamp, type_, content in all_contents:
                date, time = timestamp.split(' ')
                review += f"- **{date} {time}** [{type_}]: {content}\n"
        else:
            review += "- 暂无相关内容\n"
        
        # 4. 交互逻辑
        review += "\n---\n\n"
        review += "## 💬 交互反馈\n"
        review += "复盘报告已生成，您对这份报告满意吗？\n"
        review += "- 输入 '调整' 可以修改报告内容\n"
        review += "- 输入 '补充' 可以添加更多内容\n"
        review += "- 输入 '确认' 可以保存这份报告\n"
        
        return {
            "success": True,
            "message": review,
            "data": {
                "topic": topic,
                "total_records": len(records),
                "calorie_records": len(calorie_records),
                "collect_records": len(collect_records),
                "summary": summary
            }
        }

    def get_command_suggestions(self):
        return [
            "帮我记录日常 今天完成了项目汇报",
            "帮我估算热量 吃了一碗米饭",
            "帮我收藏 https://example.com",
            "帮我润色 今天天气很好",
            "给我今日日报",
            "复盘 工作进展"
        ]

class CLIPlatform:
    def __init__(self):
        self.orchestrator = OrchestratorAgent()
    
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
                
                print(f"\nAgent: {response['message']}\n")
                
            except KeyboardInterrupt:
                print("\n\n再见！")
                break
            except Exception as e:
                logger.error(f"处理异常: {e}")
                print(f"\n[错误] {str(e)}\n")

    def run_single(self, user_input: str, user_id: str = "default_user") -> Dict[str, Any]:
        return self.orchestrator.process(user_input, user_id)

    def run_json(self, json_input: str) -> str:
        try:
            data = json.loads(json_input)
            
            user_input = data.get("input", "")
            user_id = data.get("user_id", "default_user")
            
            response = self.orchestrator.process(user_input, user_id)
            
            return json.dumps(response, ensure_ascii=False, indent=2)
            
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
  python simple_humblelegend.py

  # 单条指令
  python simple_humblelegend.py --input "帮我记录今天完成了项目汇报"

  # JSON模式
  python simple_humblelegend.py --json '{"input": "给我今日日报", "user_id": "user123"}'
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
    
    args = parser.parse_args()
    
    cli = CLIPlatform()
    
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
