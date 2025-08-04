# from langchain_community.vectorstores import FAISS
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.docstore.document import Document

# # Load text file
# with open("rag_documents.txt", encoding="utf-8") as f:
#     raw_texts = f.read().split("\n\n")

# # Convert to LangChain Document format
# documents = [Document(page_content=chunk.strip()) for chunk in raw_texts if chunk.strip()]

# # Optional: chunk for better recall
# splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
# chunks = splitter.split_documents(documents)

# # Embed & store in FAISS
# vectorstore = FAISS.from_documents(chunks, OpenAIEmbeddings())
# vectorstore.save_local("faiss_index")

# print("✅ FAISS 벡터 인덱스가 성공적으로 저장되었습니다.")


from langchain_community.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
import os

# ✅ Step 1: Load and split documents
loader = TextLoader("rag_documents.txt", encoding="utf-8")
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
split_docs = text_splitter.split_documents(documents)

# ✅ Step 2: Embed and save to FAISS
embedding_model = OpenAIEmbeddings()
db = FAISS.from_documents(split_docs, embedding_model)
db.save_local("faiss_index")
print("✅ FAISS index regenerated successfully.")
