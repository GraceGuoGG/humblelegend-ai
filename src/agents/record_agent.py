"""记录Agent"""

from datetime import datetime
from sqlalchemy.orm import Session
from src.core.models import ThemeType, RecordType
from src.core.db_utils import DBUtils
from src.utils.image_recognition import ImageRecognition
from src.utils.nutrition_database import NutritionDatabase


class RecordAgent:
    """记录Agent"""
    
    def __init__(self, db: Session):
        """初始化"""
        self.db = db
        self.image_recognizer = ImageRecognition()
        self.nutrition_db = NutritionDatabase()
    
    def handle_daily_record(self, user_id: str, content: str, theme: str) -> str:
        """处理日常记录"""
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
        
        theme_type = theme_map.get(theme, ThemeType.WORK)
        
        # 添加时间戳
        timestamp = datetime.now().strftime("%H:%M")
        formatted_content = f"{timestamp}，{content}"
        
        # 创建记录
        DBUtils.create_record(self.db, user_id, formatted_content, theme_type)
        
        return f"已记录：{formatted_content}（主题：{theme_type.value}）"
    
    def handle_calorie_record(self, user_id: str, food: str) -> str:
        """处理热量记录"""
        # 检查是否是图片路径
        if food.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            # 图片识别
            food_info = self.image_recognizer.recognize_food(food)
            food_name = food_info["name"]
            if food_name == "未知食物":
                return "抱歉，无法识别图片中的食物。"
            food = food_name
        
        # 处理多种食物
        foods = food.split()
        total_calorie = 0.0
        total_protein = 0.0
        total_fat = 0.0
        total_carbs = 0.0
        total_sodium = 0.0
        details = []
        
        for f in foods:
            # 从营养数据库获取详细信息
            nutrition_info = self.nutrition_db.get_nutrition_info(f)
            calorie = nutrition_info["calorie"]
            protein = nutrition_info["protein"]
            fat = nutrition_info["fat"]
            carbs = nutrition_info["carbs"]
            sodium = nutrition_info["sodium"]
            
            total_calorie += calorie
            total_protein += protein
            total_fat += fat
            total_carbs += carbs
            total_sodium += sodium
            
            details.append(f"{f}：{calorie}千卡，蛋白质{protein}克，脂肪{fat}克，碳水{carbs}克，钠{ sodium}毫克")
        
        # 创建热量记录
        DBUtils.create_calorie_record(
            self.db, user_id, food, total_calorie, 
            total_protein, total_fat, total_carbs, total_sodium
        )
        
        detail_str = "\n".join(details)
        return f"热量估算结果：\n{detail_str}\n总计：{total_calorie}千卡，蛋白质{total_protein}克，脂肪{total_fat}克，碳水{total_carbs}克，钠{total_sodium}毫克"
    
    def handle_collection(self, user_id: str, content: str) -> str:
        """处理内容收藏"""
        # 简单判断是URL还是文本
        if content.startswith("http://") or content.startswith("https://"):
            # 收藏URL
            title = content.split("/")[-1] or "网页链接"
            DBUtils.create_collection(self.db, user_id, title, url=content)
            return f"已收藏网页：{content}"
        else:
            # 收藏文本
            title = content[:50] + "..." if len(content) > 50 else content
            DBUtils.create_collection(self.db, user_id, title, content=content)
            return f"已收藏文本：{title}"
    
    def handle_polish(self, user_id: str, text: str, style: str = "default") -> str:
        """处理文本润色"""
        # 简单的润色逻辑
        polished_text = self._polish_text(text, style)
        
        # 创建润色记录
        DBUtils.create_polish_record(self.db, user_id, text, polished_text, style)
        
        return f"润色前：{text}\n润色后：{polished_text}"
    
    def _polish_text(self, text: str, style: str) -> str:
        """文本润色逻辑"""
        # 这里应该调用LLM进行润色，现在使用简单的规则
        if style == "formal":
            # 正式风格
            return text.replace("你好", "您好").replace("谢谢", "感谢").replace("没问题", "没问题的")
        elif style == "friendly":
            # 友好风格
            return text + "！希望对您有帮助～"
        else:
            # 默认风格
            return text