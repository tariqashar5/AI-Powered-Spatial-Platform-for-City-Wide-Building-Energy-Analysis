
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from modules.sql_chain import generate_sql
from modules.db_executor import execute_sql_query
from modules.summarizer_interactive import summarize_result
from modules.hybrid_summary import hybrid_summary
from modules.utils import is_explain_query, postprocess_sql
from modules.rag_chain import get_rag_answer, is_hybrid_query
import numpy as np


app = FastAPI(
    title="Daegu Building & Energy QA API",
    description="A natural language question-answering API using SQL, RAG, and Hybrid summarization for Daegu energy data.",
    version="1.0.0"
)

# Optional: enable CORS if used from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import numpy as np

@app.get("/qa")
def qa(q: str = Query(..., description="질문 입력 (자연어로 대구시 건물/에너지 관련 질의)")):
    
    print("🔥 QA route hit")
    print("➡️  Received question:", q)

    try:
        if is_hybrid_query(q):
            route = "Hybrid"
            sql = generate_sql(q)
            sql = postprocess_sql(sql)
            df = execute_sql_query(sql)
            if not df.empty:
                answer = hybrid_summary(q, df)
                df_cleaned = df.replace({np.nan: None, np.inf: None, -np.inf: None})
                return {
                    "question": q,
                    "route": route,
                    "generated_sql": sql,
                    # "rows": df.to_dict(orient="records"),
                    "rows": df_cleaned.to_dict(orient="records"),
                    "context": [],
                    "answer": answer
                }
            else:
                context, answer = get_rag_answer(q)
                return {
                    "question": q,
                    "route": "RAG",
                    "generated_sql": sql,
                    "rows": [],
                    "context": context,
                    "answer": answer
                }

        elif not is_explain_query(q):
            route = "SQL"
            sql = generate_sql(q)
            sql = postprocess_sql(sql)
            df = execute_sql_query(sql)
            if not df.empty:
                answer = summarize_result(q, df)
                df_cleaned = df.replace({np.nan: None, np.inf: None, -np.inf: None})
                return {
                    "question": q,
                    "route": route,
                    "generated_sql": sql,
                    # "rows": df.to_dict(orient="records"),
                    "rows": df_cleaned.to_dict(orient="records"),
                    "context": [],
                    "answer": answer
                }
            else:
                context, answer = get_rag_answer(q)
                return {
                    "question": q,
                    "route": "RAG",
                    "generated_sql": sql,
                    "rows": [],
                    "context": context,
                    "answer": answer
                }

        else:
            context, answer = get_rag_answer(q)
            return {
                "question": q,
                "route": "RAG",
                "generated_sql": None,
                "rows": [],
                "context": context,
                "answer": answer
            }

    except Exception as e:
        return {
            "question": q,
            "route": "ERROR",
            "generated_sql": None,
            "rows": [],
            "context": [],
            "answer": f"[오류 발생]: {str(e)}"
        }
