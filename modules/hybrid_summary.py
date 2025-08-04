import pandas as pd
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# Initialize the model
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Prompt: combines SQL result + question for explanation
hybrid_prompt = PromptTemplate.from_template("""
질문:
{question}

관련된 SQL 결과 (표 일부):
{sql_result}

위 데이터를 바탕으로 사용자 질문에 대한 설명형 요약을 한국어로 2~4문장으로 작성하세요.
""")

chain = hybrid_prompt | llm


def hybrid_summary(question, df: pd.DataFrame) -> str:
    try:
        # If result is small, just return basic summary via LLM
        if df.shape[0] <= 5 and df.shape[1] <= 5:
            result_str = df.to_string(index=False)
            return chain.invoke({
                "question": question,
                "sql_result": result_str
            }).content.strip()

        response = ""

        # Detect if grouped result (based on common column names)
        group_cols = [col for col in df.columns if "구" in col or "동" in col or "용도" in col or "지역" in col]
        numeric_cols = df.select_dtypes(include="number").columns.tolist()

        if group_cols and numeric_cols:
            # 📊 주요 그룹 요약
            response += "📊 주요 분포:\n"
            top_rows = df.head(5)
            for _, row in top_rows.iterrows():
                label = ", ".join(str(row[col]) for col in group_cols)
                numbers = [f"{col}: {row[col]:,.0f}" for col in numeric_cols if pd.notnull(row[col])]
                response += f"- {label} → {' / '.join(numbers)}\n"

            # 📈 수치 요약
            response += "\n📈 수치 요약:\n"
            stats = df[numeric_cols].describe().T
            for col in numeric_cols:
                if col in stats.index:
                    mean_val = stats.loc[col, "mean"]
                    response += f"- {col} 평균: {mean_val:,.1f}\n"

        else:
            # Fallback: use LLM to summarize
            result_str = df.head(10).to_string(index=False)
            llm_response = chain.invoke({
                "question": question,
                "sql_result": result_str
            }).content.strip()
            response += f"📄 LLM 요약:\n{llm_response}"

        return response.strip()

    except Exception as e:
        return f"[Hybrid 요약 실패]: {e}"
