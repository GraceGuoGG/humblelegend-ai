"""
热量估算Agent
识别食物图片/文本，计算营养成分
"""

from typing import Any, Dict, List, Optional
from loguru import logger

from ..core.config import Config
from ..core.llm import get_llm_service


class CalorieAgent:
    DEFAULT_NUTRITION = {
        "米饭": {"calories": 116, "protein": 2.6, "fat": 0.3, "carbs": 25.9, "sodium": 2, "default_weight": 150},
        "面条": {"calories": 137, "protein": 4.5, "fat": 0.5, "carbs": 28, "sodium": 5, "default_weight": 200},
        "馒头": {"calories": 221, "protein": 7, "fat": 1.1, "carbs": 47, "sodium": 3, "default_weight": 100},
        "鸡蛋": {"calories": 144, "protein": 13.3, "fat": 8.8, "carbs": 2.8, "sodium": 131, "default_weight": 50},
        "牛奶": {"calories": 54, "protein": 3, "fat": 3.2, "carbs": 3.4, "sodium": 37, "default_weight": 250},
        "苹果": {"calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14, "sodium": 1, "default_weight": 150},
        "香蕉": {"calories": 93, "protein": 1.2, "fat": 0.2, "carbs": 21, "sodium": 1, "default_weight": 100},
        "鸡肉": {"calories": 167, "protein": 19.3, "fat": 9.4, "carbs": 1.3, "sodium": 63, "default_weight": 100},
        "猪肉": {"calories": 143, "protein": 20.3, "fat": 6.2, "carbs": 0, "sodium": 55, "default_weight": 100},
        "牛肉": {"calories": 125, "protein": 20, "fat": 4.2, "carbs": 0, "sodium": 53, "default_weight": 100},
        "鱼": {"calories": 104, "protein": 18.5, "fat": 2.5, "carbs": 0, "sodium": 50, "default_weight": 100},
        "蔬菜": {"calories": 25, "protein": 2, "fat": 0.2, "carbs": 4, "sodium": 20, "default_weight": 100},
        "豆腐": {"calories": 81, "protein": 8.1, "fat": 3.7, "carbs": 4.2, "sodium": 7, "default_weight": 100},
    }
    
    def __init__(self, config: Config):
        self.config = config
        self.llm = get_llm_service()
    
    def estimate(self, content: str, images: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        if images and len(images) > 0:
            return self._estimate_from_image(content, images)
        else:
            return self._estimate_from_text(content)
    
    def _estimate_from_image(self, content: str, images: List[Dict[str, Any]]) -> Dict[str, Any]:
        image = images[0]
        image_url = image.get("url") or image.get("path")
        
        if not image_url:
            return {
                "success": False,
                "message": "无法获取图片地址",
            }
        
        prompt = """请识别这张图片中的食物，并估算其重量和营养成分。
请以JSON格式返回，包含以下字段：
- food_name: 食物名称
- estimated_weight: 估算重量(克)
- calories: 热量(千卡)
- protein: 蛋白质(克)
- fat: 脂肪(克)
- carbs: 碳水化合物(克)
- sodium: 钠(毫克)

只返回JSON，不要其他内容。"""
        
        try:
            response = self.llm.chat_with_image(prompt, image_url)
            
            import json
            import re
            
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                result["success"] = True
                result["source"] = "image"
                return result
            else:
                logger.warning(f"无法解析LLM响应: {response}")
                return self._estimate_from_text(content)
                
        except Exception as e:
            logger.error(f"图片识别失败: {e}")
            return self._estimate_from_text(content)
    
    def _estimate_from_text(self, content: str) -> Dict[str, Any]:
        if not content:
            return {
                "success": False,
                "message": "请提供食物描述",
            }
        
        food_name, weight = self._parse_food_description(content)
        
        nutrition = self._lookup_nutrition(food_name)
        
        if nutrition is None:
            return self._estimate_with_llm(content)
        
        if weight is None:
            weight = nutrition.get("default_weight", 100)
        
        multiplier = weight / 100
        
        return {
            "success": True,
            "food_name": food_name,
            "estimated_weight": weight,
            "calories": round(nutrition["calories"] * multiplier, 1),
            "protein": round(nutrition["protein"] * multiplier, 1),
            "fat": round(nutrition["fat"] * multiplier, 1),
            "carbs": round(nutrition["carbs"] * multiplier, 1),
            "sodium": round(nutrition["sodium"] * multiplier, 1),
            "source": "database",
        }
    
    def _parse_food_description(self, content: str) -> tuple:
        import re
        
        weight_patterns = [
            r"(\d+(?:\.\d+)?)\s*(克|g|G)",
            r"(\d+(?:\.\d+)?)\s*(斤|公斤|kg|KG)",
            r"(一碗|一碗饭|一碗面)",
            r"(一个|一个鸡蛋|一个苹果)",
        ]
        
        weight = None
        food_name = content
        
        for pattern in weight_patterns:
            match = re.search(pattern, content)
            if match:
                if match.group(1) in ["一碗", "一碗饭", "一碗面"]:
                    weight = 200
                    food_name = content.replace(match.group(0), "").strip()
                elif match.group(1) in ["一个", "一个鸡蛋", "一个苹果"]:
                    weight = 50 if "鸡蛋" in match.group(0) else 150
                    food_name = content.replace(match.group(0), "").strip()
                else:
                    value = float(match.group(1))
                    unit = match.group(2)
                    if unit in ["斤"]:
                        weight = value * 500
                    elif unit in ["公斤", "kg", "KG"]:
                        weight = value * 1000
                    else:
                        weight = value
                    food_name = content.replace(match.group(0), "").strip()
                break
        
        food_name = food_name.strip() or content
        
        return food_name, weight
    
    def _lookup_nutrition(self, food_name: str) -> Optional[Dict[str, Any]]:
        for key, nutrition in self.DEFAULT_NUTRITION.items():
            if key in food_name or food_name in key:
                return nutrition
        
        for key, nutrition in self.DEFAULT_NUTRITION.items():
            if any(char in food_name for char in key):
                return nutrition
        
        return None
    
    def _estimate_with_llm(self, content: str) -> Dict[str, Any]:
        prompt = f"""请分析以下食物描述，估算其营养成分。
食物描述：{content}

请以JSON格式返回，包含以下字段：
- food_name: 食物名称
- estimated_weight: 估算重量(克)
- calories: 热量(千卡)
- protein: 蛋白质(克)
- fat: 脂肪(克)
- carbs: 碳水化合物(克)
- sodium: 钠(毫克)

只返回JSON，不要其他内容。"""
        
        try:
            response = self.llm.chat([{"role": "user", "content": prompt}])
            
            import json
            import re
            
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                result["success"] = True
                result["source"] = "llm"
                return result
            else:
                logger.warning(f"无法解析LLM响应: {response}")
                return {
                    "success": False,
                    "message": "无法估算热量，请提供更详细的食物描述",
                }
                
        except Exception as e:
            logger.error(f"LLM估算失败: {e}")
            return {
                "success": False,
                "message": f"热量估算失败: {str(e)}",
            }
