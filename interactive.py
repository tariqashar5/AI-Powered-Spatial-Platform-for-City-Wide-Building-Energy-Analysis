import csv
from datetime import datetime
from modules.sql_chain import generate_sql
from modules.db_executor import execute_sql_query
from modules.summarizer import summarize_result
from modules.hybrid_summary import hybrid_summary
from modules.utils import is_explain_query, postprocess_sql
from modules.rag_chain import get_rag_answer, is_hybrid_query

# Setup logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
log_filename = f"interactive_eval_log_{timestamp}.csv"
log_fields = ["question", "route", "answer", "score"]

print("🧠 대화형 질의응답 시스템 (종료하려면 'q' 입력)\n")

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
        if is_hybrid_query(q):
            route = "Hybrid"
            sql = generate_sql(q)
            sql = postprocess_sql(sql)
            df = execute_sql_query(sql)
            if not df.empty:
                answer = hybrid_summary(q, df)
            else:
                route = "RAG"
                _, answer = get_rag_answer(q)
        elif not is_explain_query(q):
            route = "SQL"
            sql = generate_sql(q)
            sql = postprocess_sql(sql)
            df = execute_sql_query(sql)
            if not df.empty:
                answer = summarize_result(q, df)
            else:
                route = "RAG"
                _, answer = get_rag_answer(q)
        else:
            route = "RAG"
            _, answer = get_rag_answer(q)

    except Exception as e:
        route = "RAG"
        _, answer = get_rag_answer(q)

    print("\n───────────────")
    print(f"📌 질문 유형: {route}")
    print(f"❓ 질문: {q}")
    print("📤 답변:")
    print(answer.strip())
    print("───────────────")

    score = input("✅ 이 응답이 정확하거나 유용했나요? (y/n): ").strip().lower()
    if score == "y":
        correct += 1
        score_text = "good"
    else:
        score_text = "bad"
    total += 1

    with open(log_filename, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=log_fields)
        writer.writerow({
            "question": q,
            "route": route,
            "answer": answer.strip(),
            "score": score_text
        })

print("\n📊 평가 완료!")
print(f"🔢 총 질문 수: {total}")
print(f"✅ 정확한 응답 수: {correct}")
if total > 0:
    print(f"🎯 정확도: {correct / total * 100:.2f}%")
print(f"📁 결과가 '{log_filename}' 파일에 저장되었습니다.")
