"""营养数据库模块"""

import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class NutritionDatabase:
    """营养数据库类"""
    
    def __init__(self):
        """初始化"""
        self.api_key = os.getenv("USDA_API_KEY")
        self.base_url = "https://api.nal.usda.gov/fdc/v1"
    
    def get_nutrition_info(self, food_name: str) -> dict:
        """获取食物营养信息"""
        # 这里应该调用USDA FoodData Central API
        # 由于环境限制，这里返回模拟数据
        
        # 模拟营养数据库
        nutrition_data = {
            "米饭": {
                "calorie": 116.0,
                "protein": 2.6,
                "fat": 0.3,
                "carbs": 25.6,
                "sodium": 1.0
            },
            "鸡蛋": {
                "calorie": 155.0,
                "protein": 13.0,
                "fat": 11.0,
                "carbs": 1.1,
                "sodium": 124.0
            },
            "牛奶": {
                "calorie": 42.0,
                "protein": 3.4,
                "fat": 1.0,
                "carbs": 5.0,
                "sodium": 44.0
            },
            "苹果": {
                "calorie": 52.0,
                "protein": 0.3,
                "fat": 0.2,
                "carbs": 13.8,
                "sodium": 1.0
            },
            "香蕉": {
                "calorie": 89.0,
                "protein": 1.1,
                "fat": 0.3,
                "carbs": 22.8,
                "sodium": 1.0
            },
            "德芙巧克力": {
                "calorie": 546.0,
                "protein": 7.7,
                "fat": 31.7,
                "carbs": 59.2,
                "sodium": 111.0
            },
            "鱼香肉丝": {
                "calorie": 346.0,
                "protein": 21.0,
                "fat": 22.0,
                "carbs": 18.0,
                "sodium": 890.0
            }
        }
        
        # 返回营养信息
        return nutrition_data.get(food_name, {
            "calorie": 0.0,
            "protein": 0.0,
            "fat": 0.0,
            "carbs": 0.0,
            "sodium": 0.0
        })
    
    def search_food(self, query: str) -> list:
        """搜索食物"""
        # 这里应该调用USDA FoodData Central API
        # 由于环境限制，这里返回模拟数据
        return [
            {"name": "米饭", "id": "1"},
            {"name": "鸡蛋", "id": "2"},
            {"name": "牛奶", "id": "3"}
        ]