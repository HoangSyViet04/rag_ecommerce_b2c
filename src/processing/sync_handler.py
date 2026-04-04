"""
PHASE 2.2: SYNC HANDLER (ĐỒNG BỘ DỮ LIỆU SQL -> VECTOR DB)
Nhiệm vụ: Quét SQL Server, lấy danh sách sản phẩm mới/cập nhật và đồng bộ vào ChromaDB.
Có thể gắn vào Cronjob (chạy mỗi 5 phút) hoặc gọi qua Webhook khi Admin lưu sản phẩm.
"""

import os 
from sqlalchemy import create_engine , text
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# import cau hinh
from src.core.config import settings

def sync_products_to_vector_db():
    print("[1] Đang khởi động tiến trình Đồng bộ (Sync)...")

    # 1. Kết nối SQL Server bằng SQLAlchemy Engine
    try: 
        engine = create_engine(settings.SQL_DATABASE_URL)
        conn = engine.connect()
        print("-> Kết nối SQL Server thành công")
    except Exception as e:
        print(f"[!] Lỗi kết nối SQL Server:", e)
        return
    
    # 2. Khởi tạo kết nối tới Bán cầu não phải (ChromaDB)
    db_path = os.path.join(os.path.dirname(os.path.dirname((os.path.dirname(os.path.abspath(__file__))))),'data','chroma_db')
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key= settings.GEMINI_API_KEY
    )
    vectorstore = Chroma(
        persist_directory= db_path,
        embedding_function= embeddings
    )
    print("-> Kết nối ChromaDB thành công")

    # 3. Kéo dữ liệu từ SQL Server
    print("[2] Truy xuất các sản phẩm đang Active từ SQL...")
    try:
        query = text("SELECT product_id, name, description, category ,price, status FROM products")
        result = conn.execute(query).mappings().all()
        print(f" -> Lấy thành công {len(result)} sản phẩm.")
    except Exception as e: 
        print(f"[!] Lỗi truy vấn SQL Server:", e)
        conn.close()
        return
    
    # 4. Xử lý logic đồng bộ (Thêm/Cập nhật Vector)
    print("[3] Bắt đầu đồng bộ vào ChromaDB...")
    
    active_texts, active_metas, active_ids = [], [], []
    inactive_ids  = []

    for row in result:
        # ID phải là string để lưu vào Chroma
        doc_id = f"prod_{row['product_id']}"

        if row['status'] == 'active':
            content = f"sản phẩm: {row['name'] } . Phân loại: {row['category']} . Chi tiết: {row['description']} "
            active_texts.append(content)
            active_ids.append(doc_id)
            active_metas.append({
                "source": "sql_server",
                "product_id": row["product_id"],
                "name": row["name"],
                "category": row["category"],
                "price": float(row["price"])
            })
        else:
            inactive_ids.append(doc_id)
        print( f" Sẵn sàng đồng bộ (Sync):[{doc_id}] {row['name']} | Giá: {row['price']}đ")

    if active_texts:
        # Add_texts sẽ tự động ghi đè/cập nhật nếu ID đã tồn tại trong ChromaDB
        vectorstore.add_texts(texts=active_texts, 
                              metadatas= active_metas,
                              ids = active_ids)
        print(f"-> Đồng bộ thành công {len(active_texts)} sản phẩm vào ChromaDB.")
    if inactive_ids:
        try: # try -except để tránh lỗi nếu có ID không tồn tại trong ChromaDB
            vectorstore.delete(ids=inactive_ids)
            print(f"-> Đã xóa {len(inactive_ids)} sản phẩm không còn active khỏi ChromaDB")
        except Exception as e:
            print(f"-> Lỗi khi xóa sản phẩm khỏi ChromaDB:{e}")

    # 5. Đóng kết nối SQL Server
    conn.close()
    print("[4] Hoàn tất tiến trình Đồng bộ (Sync).")

if __name__ == "__main__":
    sync_products_to_vector_db()
