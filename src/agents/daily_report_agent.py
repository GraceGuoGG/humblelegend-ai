"""日报Agent"""

from datetime import datetime
from sqlalchemy.orm import Session
from src.core.db_utils import DBUtils
from src.core.models import ThemeType
from src.utils.chart_generator import ChartGenerator


class DailyReportAgent:
    """日报Agent"""
    
    def __init__(self, db: Session):
        """初始化"""
        self.db = db
        self.chart_generator = ChartGenerator()
    
    def generate_daily_report(self, user_id: str) -> str:
        """生成今日日报"""
        today = datetime.now()
        
        # 获取今日记录
        records = DBUtils.get_records_by_date(self.db, user_id, today)
        calorie_records = DBUtils.get_calorie_records_by_date(self.db, user_id, today)
        collections = DBUtils.get_collections_by_date(self.db, user_id, today)
        polish_records = DBUtils.get_polish_records_by_date(self.db, user_id, today)
        
        # 生成日报
        report = []
        report.append(f"# 今日日报 ({today.strftime('%Y-%m-%d')})")
        report.append("")
        
        # 数据卡片
        report.append("## 📊 数据卡片")
        report.append("- **今日记录数**: " + str(len(records)))
        report.append("- **热量摄入**: " + str(sum(r.calorie for r in calorie_records)) + " 千卡")
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
        for theme in ThemeType:
            theme_records = [r for r in records if r.theme == theme]
            if theme_records:
                report.append(f"### {theme.value}")
                for record in theme_records:
                    report.append(f"- {record.content}")
                report.append("")
        
        # 趋势图表
        report.append("## 📈 趋势图表")
        # 获取近7天的记录
        all_records = DBUtils.get_all_records(self.db, user_id, days=7)
        chart = self.chart_generator.generate_trend_chart(all_records, days=7)
        report.append("```mermaid")
        report.append(chart)
        report.append("```")
        report.append("")
        
        # 交互逻辑
        report.append("## 💬 交互反馈")
        report.append("- 回复【调整】修改日报内容")
        report.append("- 回复【补充】添加更多内容")
        report.append("- 回复【确认】确认日报内容")
        report.append("- 回复【导出】导出日报为MD/PDF")
        
        return "\n".join(report)
    
    def _generate_summary(self, records, calorie_records, collections, polish_records) -> str:
        """生成当日总结"""
        # 简单的总结逻辑
        summary_parts = []
        
        if records:
            summary_parts.append(f"今日共记录了{len(records)}条内容，涵盖了工作、生活等多个方面。")
        
        if calorie_records:
            total_calorie = sum(r.calorie for r in calorie_records)
            summary_parts.append(f"今日热量摄入为{total_calorie}千卡，")
            if total_calorie > 2000:
                summary_parts.append("略高于推荐摄入量，请注意控制。")
            else:
                summary_parts.append("在合理范围内。")
        
        if collections:
            summary_parts.append(f"今日收藏了{len(collections)}条内容，")
            if any(c.url for c in collections):
                summary_parts.append("包括一些有价值的网页链接。")
            else:
                summary_parts.append("包括一些重要的文本信息。")
        
        if polish_records:
            summary_parts.append(f"今日润色了{len(polish_records)}条文本，提升了表达效果。")
        
        if not summary_parts:
            return "今日暂无记录，建议您开始记录今天的生活和工作。"
        
        return " ".join(summary_parts)