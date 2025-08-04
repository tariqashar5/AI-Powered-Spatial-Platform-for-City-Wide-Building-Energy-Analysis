# modules/summarizer.py
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
import os
import time
from openai import RateLimitError

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))

template = """
질문:
{question}

SQL 실행 결과 (일부):
{result}

→ 위 내용을 한국어로 2~3문장 요약해주세요.
"""

prompt = PromptTemplate(input_variables=["question", "result"], template=template)
chain = LLMChain(llm=llm, prompt=prompt)


## ---- NO AUTOMATIC RETRY IF OPENAI RETURNS RATE LIMIT REACHED
# def summarize_result(question, df):
#     # Limit rows to avoid exceeding token limit
#     df_trimmed = df.head(10)
#     result_str = df_trimmed.to_string(index=False)
#     try:
#         return chain.run({"question": question, "result": result_str})
#     except Exception as e:
#         return f"[요약 실패]: {e}"

#---- AUTOMATIC RETRY IF OPENAI RETURNS RATE LIMIT REACHED
def summarize_result(question, df, max_retries=3):
    df_trimmed = df.head(10)
    result_str = df_trimmed.to_string(index=False)
    prompt_input = {"question": question, "result": result_str}

    for attempt in range(max_retries):
        try:
            return chain.run(prompt_input)
        except Exception as e:
            if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"[Retrying due to rate limit] Attempt {attempt + 1}, waiting {wait}s")
                time.sleep(wait)
            else:
                return f"[요약 실패]: {e}"