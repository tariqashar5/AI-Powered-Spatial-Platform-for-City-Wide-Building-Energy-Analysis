# import requests

# question = "2023년 기준 대구시 각 구별 평균 전기 사용량을 비교해주세요."
# response = requests.get("http://localhost:8000/qa", params={"q": question})

# try:
#     res_json = response.json()
#     print("\n✅ 질문:", res_json.get("question"))
#     print("📤 최종 응답:", res_json.get("answer"))
#     print("📊 결과 수:", len(res_json.get("rows", [])))
# except Exception as e:
#     print("❌ Error:", str(e))



# generate_schema.py
import json
from utils import get_schema_dict

# Set your actual database path
db_path = "D:/AI - KNU/Undergrad Project Mentoring (NineWatt)/new energy project/energy_map.db"

schema = get_schema_dict(db_path)

# Save to db_schema.json in your project root (or wherever your code expects it)
with open("db_schema.json", "w", encoding="utf-8") as f:
    json.dump(schema, f, ensure_ascii=False, indent=2)

print("✅ db_schema.json has been updated.")
