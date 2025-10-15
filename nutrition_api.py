import requests

API_KEY = "ReBadYG8KNa2FFardRIcggJzuM79U41hH6lfc9JB"   # 👈 Thay bằng API key bạn nhận được
BASE_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

def get_nutrition_info(fruit_name):
    try:
        params = {
            "api_key": API_KEY,
            "query": fruit_name,
            "pageSize": 1
        }
        r = requests.get(BASE_URL, params=params)
        data = r.json()

        if "foods" not in data or len(data["foods"]) == 0:
            return {"error": "Không tìm thấy thông tin dinh dưỡng."}

        food = data["foods"][0]
        nutrients = {n["nutrientName"]: n["value"] for n in food.get("foodNutrients", [])}

        return {
            "name": food.get("description", fruit_name),
            "calories": f"{nutrients.get('Energy', 'N/A')} kcal",
            "carbs": f"{nutrients.get('Carbohydrate, by difference', 'N/A')} g",
            "protein": f"{nutrients.get('Protein', 'N/A')} g",
            "fat": f"{nutrients.get('Total lipid (fat)', 'N/A')} g",
        }
    except Exception as e:
        return {"error": str(e)}
