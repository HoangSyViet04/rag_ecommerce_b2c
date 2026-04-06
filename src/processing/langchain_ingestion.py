"""
PHASE 2: HYBRID DATA INGESTION (MULTI-FORMAT)
Quét thư mục data/raw/, đọc tất cả file PDF, DOCX, TXT.
Nạp dữ liệu vào ChromaDB (Vector) và BM25 (Keyword).
"""

import re
import os 
import pickle
from typing import List
import shutil

# import dàn Loader của langchain 
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_core.documents import Document

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_chroma import Chroma
from rank_bm25 import BM25Okapi


# import config
from src.core.config import settings

def clean_text(text: str) -> str:
    """Dọn rác khoảng trắng thừa từ file PDF (Ví dụ: 'Đ ỔI' -> 'ĐỔI')"""
    # Xóa các khoảng trắng vô lý giữa các chữ cái tiếng Việt (nếu cần thiết có thể tùy chỉnh)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def load_and_clean(loader):
    docs = loader.load()
    for doc in docs:
        doc.page_content = clean_text(doc.page_content)
    return docs

def load_all_documents(directory_path: str) -> List[Document]:
    """
    Hàm quét thư mục và tự động chọn Loader phù hợp với từng loại đuôi file.
    Có xử lý try-except để nếu 1 file hỏng thì hệ thống không bị crash toàn bộ.
    """
    all_docs = []
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Đã tạo thư mục {directory_path}. Hãy thả file PDF, DOCX, TXT vào đây")
        return all_docs
    
    print(f"[*] Đang quét thư mục {directory_path}")
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        ext = os.path.splitext(filename)[1].lower()

        try: 
            if ext == '.txt':
                loader = load_and_clean(TextLoader(file_path,encoding='utf-8'))
                all_docs.extend(loader)
                print(f"[+] Đã nạp file (txt): {filename}")
            elif ext in ['.docx', '.doc']:
                loader = load_and_clean(Docx2txtLoader(file_path))
                all_docs.extend(loader)
                print(f"[+] Đã nạp file (docx): {filename}")
            elif ext == '.pdf':
                loader = load_and_clean(PyPDFLoader(file_path))
                all_docs.extend(loader)
                print(f"[+] Đã nạp file (pdf): {filename}")
            else:
                print(f" - Bỏ qua định dạng không hỗ trợ: {filename}")
        except Exception as e:
            print(f"[!] Lỗi khi đọc file {filename}: {e}")

    return all_docs


def run_hybrid_ingestion():
    print(f"[1] Khởi tạo")
    embeddings = HuggingFaceEmbeddings(
        model_name="bkai-foundation-models/vietnamese-bi-encoder",
        encode_kwargs={'normalize_embeddings': True}
    )
    text_splitter = SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type= "standard_deviation"
    )

    print(f"[2] Đọc tài liệu thô từ nhiều định dạng")
    raw_dir =  os.path.join(os.path.dirname(os.path.dirname((os.path.dirname(os.path.abspath(__file__))))),'data','raw')
    docs = load_all_documents(raw_dir)

    if not docs:
        print("Không có tài liệu nào để xử lý. Dừng chương trình")
        return
    
    print(f"[3] Băm nhỏ {len(docs)} trang tài liệu (Semantic Chunking)...")
    chunks = text_splitter.split_documents(docs)
    print(f" -> Đã cắt thành {len(chunks)} đoạn ngữ nghĩa hoàn chỉnh") 

    print("[4] Xây dựng Não phải (Vector Store - ChromaDB)...")
    db_path = os.path.join(os.path.dirname(os.path.dirname((os.path.dirname(os.path.abspath(__file__))))),'data','chroma_db')

    if os.path.exists(db_path):
        shutil.rmtree(db_path)
        print(" -> Đã dọn dẹp Database cũ.")

        
    vectorstore = Chroma.from_documents(
        documents= chunks,
        embedding=embeddings,
        persist_directory= db_path
    )
    print(" -> Nạp ChromaDB thành công")

    print("[5] Xây dựng Não trái (Keyword Store - BM25)...")
    # Dùng Regex để lột bỏ toàn bộ dấu câu (chấm, phẩy, ngoặc...), chỉ lấy chữ và số
    tokenized_corpus = [re.findall(r'\w+', chunk.page_content.lower()) for chunk in chunks]
    bm25 = BM25Okapi(tokenized_corpus)

    bm25_path = os.path.join(os.path.dirname(os.path.dirname((os.path.dirname(os.path.abspath(__file__))))),'data','bm25_index.pkl')
    with open(bm25_path, "wb") as f:
        pickle.dump({"bm25": bm25, "chunks": chunks}, f)
    print(f" -> Lưu chỉ mục BM25 thành công tại {bm25_path}")

    print("[6] Hoàn tất quá trình Hybrid Ingestion. Dữ liệu đã sẵn sàng cho truy vấn RAG")

if __name__ == "__main__":
    run_hybrid_ingestion()