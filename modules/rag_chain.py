# modules/rag_chain.py

from langchain_community.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
import os


# Ensure we get absolute path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAISS_PATH = os.path.join(ROOT_DIR, "faiss_index")

# Load FAISS index
def load_faiss_index():
    # vectorstore_path = "faiss_index"
    print("📂 Current Working Dir:", os.getcwd())
    print("📁 FAISS Full Path:", FAISS_PATH)
    if not os.path.exists(os.path.join(FAISS_PATH, "index.faiss")):
        raise ValueError("❌ FAISS index not found at expected path. Please rebuild.")
    
    embeddings = OpenAIEmbeddings()
    retriever = FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True).as_retriever(search_kwargs={"k": 10})
    return retriever

# Prompt template for explanation-style answers
EXPLAIN_PROMPT = PromptTemplate.from_template("""
다음은 대구시 건물, 에너지 사용량, 인구 통계에 대한 질의입니다. 질문에 답하기 위해 참고 문서를 바탕으로 정확하고 구체적인 정보를 제공하세요. 추측하지 마세요.

[질문]
{question}

[참고 문서]
{context}

[답변]
""")

# Build QA chain using retriever
def build_rag_chain():
    llm = ChatOpenAI(temperature=0, model="gpt-4")
    retriever = load_faiss_index()
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": EXPLAIN_PROMPT}
    ), retriever

# Call this to get final RAG answer
def get_rag_answer(question: str):
    qa_chain, retriever = build_rag_chain()
    docs = retriever.get_relevant_documents(question)
    context = [doc.page_content for doc in docs]
    answer = qa_chain.run({"query": question})
    return context, answer

# Hybrid-eligible queries (custom rule-based example)
def is_hybrid_query(q: str) -> bool:
    keywords = ["설명", "분석", "이유", "차이", "특성", "추세", "경향", "요인"]
    return any(k in q for k in keywords)
