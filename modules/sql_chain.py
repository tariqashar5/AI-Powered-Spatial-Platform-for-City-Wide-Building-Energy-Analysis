# modules/sql_chain.py

from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from modules.utils import load_schema_string
import traceback

# 1. Prompt with schema and question
sql_prompt = PromptTemplate.from_template("""
다음은 대구시 건축물/에너지/인구 데이터베이스의 테이블 스키마입니다.

{schema}

사용자가 다음과 같은 질문을 했습니다:

질문: {question}

위 질문에 답하기 위해 SQL 쿼리를 작성하세요.
- 실제 존재하는 테이블과 컬럼만 사용하세요.
- 쿼리만 출력하고 주석, 설명, 기타 문장은 넣지 마세요.
- 테이블 이름은 다음 중 하나여야 합니다: building_daegu, energy_daegu, population
- 컬럼 이름이 괄호나 특수문자를 포함하는 경우, 반드시 큰따옴표(")로 감싸서 사용하세요.

SQL:
""")

# 2. LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# 3. Chain
sql_chain = LLMChain(llm=llm, prompt=sql_prompt)

# 4. Main function
def generate_sql(question: str) -> str:
    try:
        # ✅ Load schema
        schema_str = load_schema_string("db_schema.json")

        # ✅ Optional: truncate if too long
        schema_lines = schema_str.split("\n")
        schema_str = "\n".join(schema_lines[:500])

        # ✅ Generate SQL
        print("🧠 Generating SQL using LLM...")
        sql = sql_chain.run({"question": question, "schema": schema_str})
        print("✅ Generated SQL:", sql)
        return sql.strip()

    except Exception as e:
        print("❌ SQL generation error:", str(e))
        traceback.print_exc()
        return f"[오류 발생]: {str(e)}"
