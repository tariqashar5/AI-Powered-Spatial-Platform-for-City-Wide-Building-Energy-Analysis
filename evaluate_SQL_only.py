# evaluate.py
import pandas as pd
from modules.sql_chain import generate_sql
from modules.db_executor import execute_sql_query
from modules.summarizer import summarize_result
from modules.utils import is_explain_query, postprocess_sql

import json

def load_classification_examples(json_path="classification_examples.json"):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    grouped = {"A": [], "B": [], "C": [], "D": [], "E": [], "F": [], "G": [], "H": []}

    for idx, item in enumerate(data):
        # Group by block index: A = 0–9, B = 10–19, ..., H = 70–99
        block = idx // 10
        label = chr(ord('A') + block) if block < 7 else 'H'
        grouped[label].append(item["question"])

    return grouped

benchmark_questions = load_classification_examples()

# To run only one question per type (A–H), set this to True
TEST_MODE = True

if TEST_MODE:
    benchmark_questions = {k: [v[0]] for k, v in benchmark_questions.items() if v}


results = []

for qtype, qlist in benchmark_questions.items():
    for q in qlist:
        entry = {"type": qtype, "question": q}
        try:
            if not is_explain_query(q):
                sql = generate_sql(q)
                sql = postprocess_sql(sql)
                entry["generated_sql"] = sql

                if sql.strip().startswith("-- ERROR"):
                    entry["route"] = "SQL"
                    entry["rows"] = None
                    entry["answer"] = sql
                    entry["success"] = False
                else:
                    df = execute_sql_query(sql)
                    entry["route"] = "SQL"
                    entry["rows"] = len(df)
                    entry["answer"] = summarize_result(q, df)
                    entry["success"] = True
            else:
                entry["route"] = "EXPLAIN"
                entry["rows"] = None
                entry["answer"] = "RAG explanation-type query not supported in evaluate.py yet"
                entry["success"] = False
        except Exception as e:
            entry["route"] = "ERROR"
            entry["rows"] = None
            entry["answer"] = f"Execution failed: {e}"
            entry["success"] = False

        results.append(entry)

        print(f"\n--- [{qtype}] {q}")
        print("SQL:", entry.get("generated_sql", "❌"))
        print("Answer:", entry["answer"])

# Save results
df_results = pd.DataFrame(results)
df_results.to_csv("evaluation_results.csv", index=False)
print("\n✅ Evaluation complete. Saved to evaluation_results.csv")
