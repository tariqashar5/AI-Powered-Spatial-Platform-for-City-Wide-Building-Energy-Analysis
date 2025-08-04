# interactive_api.py

import requests
import csv
from datetime import datetime

# Setup log file
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
log_filename = f"interactive_api_log_{timestamp}.csv"
log_fields = ["question", "route", "answer", "score"]

print("🧠 API 연동 대화형 질의응답 시스템 (서버가 실행 중이어야 함)\n❓ 종료하려면 'q' 입력\n")

with open(log_filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=log_fields)
    writer.writeheader()

correct = 0
total = 0

while True:
    q = input("❓ 질문을 입력하세요: ").strip()
    if q.lower() in {"q", "quit", "exit"}:
        break

    try:
        # Call FastAPI endpoint
        response = requests.get("http://localhost:8000/qa", params={"q": q})
        res_json = response.json()

        route = res_json.get("route", "UNKNOWN")
        answer = res_json.get("answer", "[응답 없음]")

        print("\n📌 질문 유형:", route)
        print("📤 최종 응답:\n", answer.strip())
        print("───────────────")

        while True:
            score = input("✅ 이 응답이 정확하거나 유용했나요? (y/n): ").strip().lower()
            if score == "y":
                score_text = "good"
                break
            elif score == "n":
                score_text = "bad"
                break
            else:
                print("Please enter either 'y' or 'n'.")

        if score_text == "good":
            correct += 1
        total += 1
        print("===============\n")

        # Save result to CSV
        with open(log_filename, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=log_fields)
            writer.writerow({
                "question": q,
                "route": route,
                "answer": answer.strip(),
                "score": score_text
            })

    except Exception as e:
        print("❌ 오류 발생:", str(e))
        continue

# Summary
print("\n📊 평가 완료!")
print(f"🔢 총 질문 수: {total}")
print(f"✅ 정확한 응답 수: {correct}")
if total > 0:
    print(f"🎯 정확도: {correct / total * 100:.2f}%")
print(f"📁 결과가 '{log_filename}' 파일에 저장되었습니다.")
