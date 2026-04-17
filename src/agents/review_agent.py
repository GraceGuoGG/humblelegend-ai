"""复盘Agent"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.core.db_utils import DBUtils
from src.core.models import ThemeType
from src.utils.chart_generator import ChartGenerator


class ReviewAgent:
    """复盘Agent"""
    
    def __init__(self, db: Session):
        """初始化"""
        self.db = db
        self.chart_generator = ChartGenerator()
    
    def generate_review_report(self, user_id: str, theme: str) -> str:
        """生成复盘报告"""
        # 转换主题
        theme_map = {
            "1": ThemeType.REST,
            "2": ThemeType.DIET,
            "3": ThemeType.WORK,
            "4": ThemeType.ENTERTAINMENT,
            "作息": ThemeType.REST,
            "饮食": ThemeType.DIET,
            "工作": ThemeType.WORK,
            "娱乐": ThemeType.ENTERTAINMENT
        }
        
        theme_type = theme_map.get(theme, None)
        
        # 获取近7天和近8周的数据
        today = datetime.now()
        seven_days_ago = today - timedelta(days=7)
        eight_weeks_ago = today - timedelta(weeks=8)
        
        # 获取数据
        if theme_type:
            records = DBUtils.get_records_by_theme(self.db, user_id, theme_type, days=56)
            calorie_records = DBUtils.get_all_calorie_records(self.db, user_id, days=56)
            collections = DBUtils.get_all_collections(self.db, user_id, days=56)
            polish_records = DBUtils.get_all_polish_records(self.db, user_id, days=56)
        else:
            records = DBUtils.get_all_records(self.db, user_id, days=56)
            calorie_records = DBUtils.get_all_calorie_records(self.db, user_id, days=56)
            collections = DBUtils.get_all_collections(self.db, user_id, days=56)
            polish_records = DBUtils.get_all_polish_records(self.db, user_id, days=56)
        
        # 生成复盘报告
        report = []
        report.append(f"# 复盘报告 - {theme if theme != '整体' else '整体情况'}")
        report.append("")
        
        # 历史数据趋势
        report.append("## 📈 历史数据趋势")
        report.append("### 近7天趋势")
        seven_day_trend = self._generate_seven_day_trend(records, calorie_records, today)
        report.append(seven_day_trend)
        report.append("")
        
        report.append("### 近8周趋势")
        eight_week_trend = self._generate_eight_week_trend(records, calorie_records, today)
        report.append(eight_week_trend)
        report.append("")
        
        # 趋势图表
        report.append("### 趋势图表")
        chart = self.chart_generator.generate_trend_chart(records, days=7)
        report.append("```mermaid")
        report.append(chart)
        report.append("```")
        report.append("")
        
        # 主题总结
        report.append("## 📝 主题总结")
        summary = self._generate_review_summary(records, calorie_records, collections, polish_records, theme_type)
        report.append(summary)
        report.append("")
        
        # 主题box
        report.append("## 📦 主题box")
        if theme_type:
            # 按时间戳排序的主题内容
            theme_records = [r for r in records if r.theme == theme_type]
            theme_records.sort(key=lambda x: x.created_at)
            for record in theme_records:
                report.append(f"- {record.created_at.strftime('%Y-%m-%d %H:%M')}: {record.content}")
        else:
            # 整体内容，按主题分类
            for theme in ThemeType:
                theme_records = [r for r in records if r.theme == theme]
                if theme_records:
                    report.append(f"### {theme.value}")
                    theme_records.sort(key=lambda x: x.created_at)
                    for record in theme_records:
                        report.append(f"- {record.created_at.strftime('%Y-%m-%d %H:%M')}: {record.content}")
                    report.append("")
        
        # 交互逻辑
        report.append("## 💬 交互反馈")
        report.append("- 回复【调整】修改复盘内容")
        report.append("- 回复【补充】添加更多内容")
        report.append("- 回复【确认】确认复盘内容")
        report.append("- 回复【导出】导出复盘为MD/PDF")
        
        return "\n".join(report)
    
    def _generate_seven_day_trend(self, records, calorie_records, today) -> str:
        """生成近7天趋势"""
        trend = []
        for i in range(7):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            # 记录数
            day_records = [r for r in records if r.created_at.date() == date.date()]
            record_count = len(day_records)
            
            # 热量摄入
            day_calories = [r for r in calorie_records if r.created_at.date() == date.date()]
            calorie_total = sum(r.calorie for r in day_calories)
            
            trend.append(f"- {date_str}: 记录{record_count}条，热量{calorie_total}千卡")
        
        return "\n".join(trend)
    
    def _generate_eight_week_trend(self, records, calorie_records, today) -> str:
        """生成近8周趋势"""
        trend = []
        for i in range(8):
            week_start = today - timedelta(weeks=i, days=today.weekday())
            week_end = week_start + timedelta(days=6)
            week_str = f"{week_start.strftime('%Y-%m-%d')} 至 {week_end.strftime('%Y-%m-%d')}"
            
            # 记录数
            week_records = [r for r in records if week_start.date() <= r.created_at.date() <= week_end.date()]
            record_count = len(week_records)
            
            # 热量摄入
            week_calories = [r for r in calorie_records if week_start.date() <= r.created_at.date() <= week_end.date()]
            calorie_total = sum(r.calorie for r in week_calories)
            
            trend.append(f"- {week_str}: 记录{record_count}条，热量{calorie_total}千卡")
        
        return "\n".join(trend)
    
    def _generate_review_summary(self, records, calorie_records, collections, polish_records, theme_type) -> str:
        """生成主题总结"""
        # 简单的总结逻辑
        summary_parts = []
        
        if records:
            summary_parts.append(f"在过去8周内，共记录了{len(records)}条内容，")
            if theme_type:
                theme_records = [r for r in records if r.theme == theme_type]
                summary_parts.append(f"其中{theme_type.value}主题的记录有{len(theme_records)}条。")
            else:
                summary_parts.append("涵盖了各个主题。")
        
        if calorie_records:
            total_calorie = sum(r.calorie for r in calorie_records)
            average_calorie = total_calorie / len(calorie_records) if calorie_records else 0
            summary_parts.append(f"热量摄入总计{total_calorie}千卡，平均每天{average_calorie:.0f}千卡，")
            if average_calorie > 2000:
                summary_parts.append("略高于推荐摄入量。")
            else:
                summary_parts.append("在合理范围内。")
        
        if collections:
            summary_parts.append(f"共收藏了{len(collections)}条内容，积累了有价值的信息。")
        
        if polish_records:
            summary_parts.append(f"共润色了{len(polish_records)}条文本，提升了表达效果。")
        
        if not summary_parts:
            return "过去8周内暂无记录，建议您开始记录生活和工作。"
        
        return " ".join(summary_parts)