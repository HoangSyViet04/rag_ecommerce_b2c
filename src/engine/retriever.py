"""
PHASE 4.2: HYBRID RETRIEVER (TRUY XUẤT LAI)
Kết hợp sức mạnh của Vector Search (Ngữ nghĩa) và BM25 (Từ khóa chính xác).
"""

from langchain.retrievers import EnsembleRetriever # Tạo một EnsembleRetriever kết hợp BM25 và Vector Search.
from langchain_community.retrievers import BM25Retriever
from src.database.vector_db import get_bm_25_store,get_vector_db

def get_hybrid_retriever():
    # 1. Não phải: Vector Retriever (Lấy top 2 kết quả gần nghĩa nhất)
    vectorstore = get_vector_db()
    vector_retriever = vectorstore.as_retriever(search_kwargs = {"k":2})

    # 2. Não trái: BM25 Retriever (cx lấy top 2 kết quả khớp nhất)
    bm25_model , chunks = get_bm_25_store()
    if not chunks:
        raise ValueError("Không load được BM25 Chunks. Hãy chạy lại Ingestion")
    
    bm25_retriever = BM25Retriever.from_documents(chunks)
    bm25_retriever.k = 2  # lấy top 2 từ khóa khớp nhất

    # 3. FUSION :Dùng EnsembleRetriever
    # Cấu hình trọng số: 70% tin vào Vector (Ý nghĩa), 30% tin vào Keyword (Từ khóa)
    ensemble_retriever = EnsembleRetriever(
        retrievers=[vector_retriever,bm25_retriever],
        weights=[0.7,0.3]
    )
    return ensemble_retriever
