"""
File này có nhiệm vụ cực kỳ đơn giản nhưng quan trọng:
Load cái thư mục data/chroma_db lên thành một đối tượng VectorStore của LangChain để các Phase sau tái
sử dụng, tránh việc cứ mỗi lần khách hỏi lại phải load DB lại từ đầu (gây tốn RAM và chậm hệ thống)
"""

"""
PHASE 3: QUẢN LÝ KẾT NỐI DATABASE VECTOR (CHROMADB)
Khởi tạo Singleton VectorStore để dùng chung cho toàn bộ hệ thống RAG.
"""

import os
import pickle
from langchain_chroma import Chroma
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.core.config import settings

def get_vector_db():
    """
    Khởi tạo và trả về đối tượng ChromaDB.
    Hàm này sẽ được gọi bởi Retriever ở Phase sau.
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="bkai-foundation-models/vietnamese-bi-encoder",
        encode_kwargs={'normalize_embeddings': True}
    )

    # Trỏ đúng vào thư mục ChromaDB đã tạo 
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"data","chroma_db")

    vectorstore = Chroma(
        persist_directory=db_path,
        embedding_function=embeddings
    )
    return vectorstore

def get_bm_25_store():
    """
    Khởi tạo và trả về đối tượng BM25 (Keyword Search).
    Dùng cho luồng Hybrid Search.
    """

    bm25_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'bm25_index.pkl')

    try:
        with open(bm25_path,"rb") as f:
            data = pickle.load(f)
            return data["bm25"], data["chunks"]
    except FileNotFoundError:
        print(f"Không tìm thấy file BM25 tại {bm25_path}. Vui lòng chạy Ingestion trước")
        return None, None
