"""
PHASE 3: AGENT TOOLS
Các công cụ (Hàm) được bọc bằng @tool để giao cho LLM sử dụng.
Docstring của hàm CỰC KỲ QUAN TRỌNG: Đây là lời giải thích để con AI biết khi nào nên dùng tool này.
"""
import json
from langchain_core.tools import tool
from sqlalchemy import text
from src.database.relational_db import get_db_connection
from src.engine.retriever import get_hybrid_retriever


@tool 
def check_product_status_and_price(product_name: str) -> str:
    """
    Hữu ích khi khách hàng hỏi về giá bán, thông tin, hoặc trạng thái (còn bán không) của một hoặc nhiều sản phẩm cụ thể.
    Input là từ khóa tên sản phẩm (ví dụ: 'Tai nghe', 'Balo').
    """
    try:
        with get_db_connection() as conn:
            # Dùng LIKE để tìm kiếm tương đối (Flexible search)
            query = text("" \
            "SELECT name , price , status FROM products WHERE name LIKE :name")
            result = conn.execute(query, {"name": f"%{product_name}%"}).mappings().all()

            if not result:
                return f"Không tìm thấy sản phẩm nào có tên giống '{product_name}'"
            
            response = []
            for row in result:
                # fomat gia tien viet nam cho dep
                price_vnd = f"{row['price']:,.0f}".replace(",", ".")
                status_vn = "Đang kinh doanh" if row['status'] == 'active' else "Ngừng kinh doanh"
                response.append(f"- Sản phẩm: {row['name']} | Giá: {price_vnd} VND | Trạng thái: {status_vn}")

            return "\n".join(response)
    except Exception as e:
        print(f"-> Lỗi hệ thống khi tra cứu dữ liệu sản phẩm: {e}")

@tool
def search_products_by_category(category_name : str) -> str:
    """
    Hữu ích khi khách hàng muốn tìm kiếm hoặc gợi ý các sản phẩm thuộc một danh mục nào đó (ví dụ: 'thoi_trang', 'dien_tu').
    Input phải là mã danh mục.
    """
    try: 
        with get_db_connection() as conn:
            query  = text("SELECT name , price FROM products WHERE category = :cat AND status = 'active'")
            result = conn.execute(query, {"cat": category_name}).mappings().all()

            if not result:
                return f"Không tìm thấy sản phẩm nào thuộc danh mục '{category_name}' đang kinh doanh."
            
            response = [f"Các sản phẩm trong danh mục {category_name}:"]
            for row in result:
                price_vnd = f"{row['price']:,.0f}".replace(",",".")
                response.append(f"- Sản phẩm: {row['name']} | Giá: {price_vnd} VND")
            return "\n".join(response)
    except Exception as e: 
        return f"-> Lỗi hệ thống khi tra cứu dữ liệu sản phẩm theo danh mục: {str(e)}"


# ==========================================
# VŨ KHÍ 3: TÌM SẢN PHẨM THEO NGỮ NGHĨA (VECTOR DB)
# ==========================================
@tool
def search_product_by_semantic(need_description: str) -> str:
    """
    Hữu ích khi khách hàng miêu tả nhu cầu, tính năng, đặc điểm mong muốn của sản phẩm (ví dụ: 'điện thoại chụp ảnh đẹp', 'balo đựng laptop', 'tai nghe cách âm').
    Input là một cụm từ khóa mô tả ngắn gọn nhu cầu đó.
    """
    try:
        # Gọi ống truy xuất lai (Vector + Keyword)
        retriever = get_hybrid_retriever()
        
        # Chỉ lấy top 3 kết quả để tránh làm quá tải bộ nhớ của Agent (Context Limit)
        # Ép kiểu retriever.retrievers[0] để set k nếu EnsembleRetriever không nhận trực tiếp
        docs = retriever.invoke(need_description)[:3]
        
        if not docs:
            return "Không tìm thấy sản phẩm nào phù hợp với nhu cầu này."
        
        # BỘ LỌC RÁC: Chỉ trích xuất Metadata và cắt ngắn nội dung để Agent dễ đọc
        results = []
        for doc in docs:
            meta = doc.metadata
            # Lọc: Chỉ lấy những chunk là dữ liệu sản phẩm (có metadata price/name)
            if 'price' in meta and 'name' in meta:
                item = {
                    "Tên sản phẩm": meta.get('name'),
                    "Giá (VNĐ)": meta.get('price'),
                    "Đặc điểm": doc.page_content[:150] + "..." # Chỉ lấy 150 ký tự đầu cho nhẹ
                }
                results.append(item)
                
        if not results:
            return "Chỉ tìm thấy thông tin chính sách, không tìm thấy sản phẩm cụ thể khớp với tính năng này."
            
        # Trả về chuỗi JSON gọn gàng cho Agent đọc
        return json.dumps(results, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return f"Lỗi hệ thống khi tìm kiếm ngữ nghĩa: {str(e)}"
    

# Đóng gói tất cả vũ khí vào một mảng để sau này giao cho Agent
ecommerce_tools = [check_product_status_and_price,search_products_by_category,search_product_by_semantic]