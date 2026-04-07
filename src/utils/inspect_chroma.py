"""
TOOL NỘI SOI CHROMADB
Mục đích: Xem thực tế dữ liệu đã được cắt (chunk) và lưu trữ như thế nào. trong vector database. Giúp hiểu rõ hơn về "não phải" của RAG, từ đó tối ưu cách cắt và lưu trữ dữ liệu.
Cách dùng: Chạy file này, nó sẽ kết nối vào thư mục chứa ChromaDB, lấy ra một số chunk đầu tiên và in ra thông tin chi tiết (ID, metadata, nội dung, độ dài) để bạn có cái nhìn trực quan về dữ liệu đã được lưu trữ. Nếu DB quá lớn, bạn có thể chỉnh sửa code để chỉ lấy một phần nhỏ (ví dụ: 3-5 chunk) để tránh quá tải.

"""

import os
from langchain_chroma import Chroma
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.core.config import settings

def inspect_vector_db():
    print(" ĐANG MỞ CHROMADB...\n")
    
    # Load Embeddings & DB
    embeddings = HuggingFaceEmbeddings(
        model_name="bkai-foundation-models/vietnamese-bi-encoder",
        encode_kwargs={'normalize_embeddings': True}
    )
    
    db_path = r"D:\Project\rag_ecommerce_b2c\data\chroma_db"
    
    try:
        vectorstore = Chroma(
            persist_directory=db_path,
            embedding_function=embeddings)
    except Exception as e:
        print(f" [X] Lỗi: {e}")
        return

    # Lấy toàn bộ dữ liệu ra (lưu ý: nếu DB quá lớn thì thêm limit)
    # Hàm get() trả về dict chứa: 'ids', 'documents', 'metadatas'
    db_content = vectorstore.get()
    
    total_chunks = len(db_content['ids'])
    print(f"TỔNG SỐ ĐOẠN (CHUNKS) TRONG NÃO PHẢI: {total_chunks}\n")
    print("-" * 50)

    # In thử 3 chunk đầu tiên để xem hình thù
    limit = min(3, total_chunks)
    for i in range(limit):
        chunk_id = db_content['ids'][i]
        text = db_content['documents'][i]
        metadata = db_content['metadatas'][i]
        
        print(f" +) CHUNK [{i+1}] | ID: {chunk_id}")
        print(f"    Metadata : {metadata}")
        print(f"    Nội dung : {text[:200]}... (đã cắt bớt cho gọn)")
        print(f"    Độ dài   : {len(text)} ký tự")
        print("-" * 50)

if __name__ == "__main__":
    inspect_vector_db()