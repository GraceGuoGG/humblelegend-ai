"""图表生成模块"""

import os
from datetime import datetime, timedelta


class ChartGenerator:
    """图表生成类"""
    
    def generate_mermaid_chart(self, data: list, chart_type: str = "line") -> str:
        """生成Mermaid图表"""
        if chart_type == "line":
            return self._generate_line_chart(data)
        elif chart_type == "bar":
            return self._generate_bar_chart(data)
        else:
            return """graph TD\n    A[图表类型不支持]"""
    
    def _generate_line_chart(self, data: list) -> str:
        """生成折线图"""
        chart = []
        chart.append("graph TD")
        
        # 生成节点
        for i, item in enumerate(data):
            date = item.get("date", f"Day{i+1}")
            value = item.get("value", 0)
            chart.append(f"    {date}({value})")
        
        # 生成连接
        for i in range(len(data) - 1):
            current_date = data[i].get("date", f"Day{i+1}")
            next_date = data[i+1].get("date", f"Day{i+2}")
            chart.append(f"    {current_date} --> {next_date}")
        
        return "\n".join(chart)
    
    def _generate_bar_chart(self, data: list) -> str:
        """生成柱状图"""
        chart = []
        chart.append("graph TD")
        
        # 生成节点
        for i, item in enumerate(data):
            date = item.get("date", f"Day{i+1}")
            value = item.get("value", 0)
            chart.append(f"    {date}({value})")
        
        return "\n".join(chart)
    
    def generate_trend_chart(self, records: list, days: int = 7) -> str:
        """生成趋势图表"""
        # 准备数据
        data = []
        today = datetime.now()
        
        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            # 统计当天的记录数
            day_records = [r for r in records if r.created_at.date() == date.date()]
            record_count = len(day_records)
            
            data.append({"date": date_str, "value": record_count})
        
        # 反转数据，使日期从早到晚
        data.reverse()
        
        return self.generate_mermaid_chart(data, "line")