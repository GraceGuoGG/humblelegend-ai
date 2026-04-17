"""文档导出模块"""

import os
from datetime import datetime


class DocumentExporter:
    """文档导出类"""
    
    def __init__(self, export_dir: str = "data/exports"):
        """初始化"""
        self.export_dir = export_dir
        # 确保导出目录存在
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_md(self, content: str, filename: str = None) -> str:
        """导出为MD文件"""
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        if not filename.endswith(".md"):
            filename += ".md"
        
        file_path = os.path.join(self.export_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return file_path
    
    def export_pdf(self, content: str, filename: str = None) -> str:
        """导出为PDF文件"""
        # 这里应该使用PDF生成库，如weasyprint或reportlab
        # 由于环境限制，这里只创建一个占位文件
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        if not filename.endswith(".pdf"):
            filename += ".pdf"
        
        file_path = os.path.join(self.export_dir, filename)
        
        # 创建占位文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("PDF文件占位符")
        
        return file_path
    
    def export_batch(self, contents: list, filenames: list = None, format: str = "md") -> list:
        """批量导出文档"""
        exported_files = []
        
        for i, content in enumerate(contents):
            filename = filenames[i] if filenames and i < len(filenames) else None
            if format == "md":
                file_path = self.export_md(content, filename)
            else:
                file_path = self.export_pdf(content, filename)
            exported_files.append(file_path)
        
        return exported_files