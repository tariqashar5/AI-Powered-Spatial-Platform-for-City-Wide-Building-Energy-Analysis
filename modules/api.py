# main.py
from fastapi import FastAPI, Query
from modules.sql_chain import generate_sql
from modules.db_executor import execute_sql_query
from modules.rag_chain import get_rag_answer
from modules.summarizer import summarize_result
from modules.utils import is_explain_query, postprocess_sql

app = FastAPI()

@app.get("/qa")
def answer_question(q: str = Query(..., description="Korean question")):
    try:
        if not is_explain_query(q):
            sql = generate_sql(q)
            sql = postprocess_sql(sql)

            if sql.strip().startswith("-- ERROR"):
                return {
                    "question": q,
                    "route": "SQL",
                    "generated_sql": sql,
                    "rows": [],
                    "answer": sql
                }

            df = execute_sql_query(sql)
            if not df.empty:
                summary = summarize_result(q, df)
                return {
                    "question": q,
                    "route": "SQL",
                    "generated_sql": sql,
                    "rows": df.to_dict(orient="records"),
                    "answer": summary
                }

    except Exception:
        pass

    # fallback to RAG
    context, summary = get_rag_answer(q)
    return {
        "question": q,
        "route": "RAG",
        "context": context,
        "answer": summary
    }
