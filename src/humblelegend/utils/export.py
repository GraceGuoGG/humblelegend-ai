"""
文档导出工具
"""

import subprocess
from pathlib import Path
from typing import Optional
from loguru import logger


def export_to_markdown(content: str, output_path: str) -> bool:
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Markdown导出成功: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Markdown导出失败: {e}")
        return False


def export_to_pdf(markdown_content: str, output_path: str) -> bool:
    try:
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(markdown_content)
            temp_md = f.name
        
        try:
            result = subprocess.run(
                ["pandoc", temp_md, "-o", output_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"PDF导出成功: {output_path}")
                return True
            else:
                logger.error(f"PDF导出失败: {result.stderr}")
                return False
        finally:
            Path(temp_md).unlink()
            
    except FileNotFoundError:
        logger.warning("pandoc未安装，尝试使用markdown-pdf")
        return _export_to_pdf_fallback(markdown_content, output_path)
    except Exception as e:
        logger.error(f"PDF导出失败: {e}")
        return False


def _export_to_pdf_fallback(markdown_content: str, output_path: str) -> bool:
    try:
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(markdown_content)
            temp_md = f.name
        
        try:
            result = subprocess.run(
                ["npx", "markdown-pdf", temp_md, "-o", output_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"PDF导出成功(markdown-pdf): {output_path}")
                return True
            else:
                logger.error(f"PDF导出失败(markdown-pdf): {result.stderr}")
                return False
        finally:
            Path(temp_md).unlink()
            
    except Exception as e:
        logger.error(f"PDF导出失败(fallback): {e}")
        return False
