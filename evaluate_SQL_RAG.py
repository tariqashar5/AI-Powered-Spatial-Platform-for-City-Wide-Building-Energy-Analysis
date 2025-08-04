import json
from modules.sql_chain import generate_sql
from modules.db_executor import execute_sql_query
from modules.summarizer import summarize_result
from modules.utils import is_explain_query, postprocess_sql
from modules.rag_chain import get_rag_answer

# Load benchmark questions
def load_examples(path="classification_examples.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

examples = load_examples()

# Limit to a test set (e.g. 10 queries)
test_set = examples[:10]


rag_test_questions = [
    "2023년 대구 북구의 에너지 사용 특징을 설명해줘.",
    "수성구는 겨울철 에너지 사용량이 많은가요?",
    "대구시에서 지역난방이 가장 널리 쓰이는 곳은 어디인가요?",
    "대구 중구의 상업시설 에너지 사용 패턴이 궁금해요."
]

# only RAG testing
for q in rag_test_questions:
    print(f"\n❓ 질문: {q}")
    try:
        _, answer = get_rag_answer(q)
        print(f"✅ [RAG 응답]: {answer}")
    except Exception as e:
        print(f"❌ RAG 실패: {e}")

# only SQL testing from input json file
# for item in test_set:
#     q = item["question"]

#     # Dynamically determine question type
#     route = "RAG" if is_explain_query(q) else "SQL"

#     print(f"\n🔹 질문 유형: {route}")
#     print(f"❓ 질문: {q}")

#     try:
#         if route == "SQL":
#             sql = generate_sql(q)
#             sql = postprocess_sql(sql)
#             df = execute_sql_query(sql)
#             if not df.empty:
#                 summary = summarize_result(q, df)
#                 print(f"✅ [SQL 응답]: {summary}")
#             else:
#                 _, answer = get_rag_answer(q)
#                 print(f"🔁 [RAG 전환]: {answer}")
#         else:
#             _, answer = get_rag_answer(q)
#             print(f"✅ [RAG 응답]: {answer}")
#     except Exception as e:
#         print(f"❌ 오류 발생: {e}")
#         _, answer = get_rag_answer(q)
#         print(f"🔁 [RAG fallback]: {answer}")
