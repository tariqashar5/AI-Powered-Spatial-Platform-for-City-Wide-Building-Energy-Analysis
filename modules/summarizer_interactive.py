# summarizer_interactive.py

import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI


# 📌 Load OpenAI model
llm = ChatOpenAI(temperature=0, model="gpt-4o")

# 🧠 Template for summarizing SQL result
summary_prompt = PromptTemplate(
    input_variables=["question", "result"],
    template="""
당신은 대구시의 건축물, 인구, 에너지 데이터 분석 전문가입니다.

아래는 사용자의 질문과 해당 질문에 대해 SQL로 조회된 표 형식의 결과입니다. 이 표를 바탕으로 아래 지침에 따라 정확하고 간결한 한국어 요약을 생성하세요:

[요약 지침]
- 핵심 수치(예: 합계, 평균, 상위값, 비율 등)를 문장에 포함하세요.
- 지역명, 연도, 용도, 에너지 종류(전기/도시가스 등)를 명확히 언급하세요.
- 결과가 비어 있다면 "조회된 결과가 없습니다"라고 응답하세요.
- 표를 그대로 나열하지 말고 요점을 요약한 문장 2~4개로 구성하세요.
- 결과가 많은 경우 상위 3개만 대표로 언급하고 그 외는 "등"으로 처리하세요.
- 숫자에는 단위를 붙이세요 (예: 15,000kWh, 120건, 12.3%)

[사용자 질문]
{question}

[SQL 결과]
{result}

[응답]
"""
)

# 🧠 Chain for LLM summarization
summary_chain = LLMChain(llm=llm, prompt=summary_prompt)


# 🎯 Entry function
def summarize_result(question: str, df: pd.DataFrame) -> str:
    if df.empty:
        return "조회된 결과가 없습니다."

    # Reduce large result for LLM context
    max_rows = 15
    display_df = df.head(max_rows).copy()

    # Simplify long column names
    display_df.columns = [col.strip()[:40] for col in display_df.columns]

    # Format result as text
    result_str = display_df.to_string(index=False)

    # Run through LLM
    summary = summary_chain.run({"question": question, "result": result_str})
    return summary.strip()
