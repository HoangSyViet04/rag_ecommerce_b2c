"""
ĐỊNH TUYẾN API (API ROUTES) :Sử dụng chuẩn Schema nâng cao từ models.chat
"""


from fastapi import APIRouter,BackgroundTasks,HTTPException
# Import Models
from src.models.chat import ChatRequest, ChatResponse
from src.models.product import ProductCreate, ProductResponse

from src.processing.sync_handler import sync_products_to_vector_db
from src.services.chat_service import process_chat_message
from src.engine.memory import save_chat_to_sql
from src.database.relational_db import get_db_connection
from sqlalchemy import text


router = APIRouter()

def save_to_sql_background(session_id:str,user_message:str, bot_reply:str):
    """
    Cho chạy ngầm dùng SQLChatMessageHistory của LangChain
    """
    try:
        print(f"-> Lưu vào SQL Memory cho session_id: {session_id}")

        # 2. Add tin nhắn vào 
        save_chat_to_sql(session_id,"user", user_message)
        save_chat_to_sql(session_id,"assistant",bot_reply)

        print(f"-> Lưu thành công lịch sử chat")
    except Exception as e:
        print(f"-> Lỗi lưu vào SQL Memory:{e}")


@router.post("/chatbot", response_model= ChatResponse)
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    # 1. Xử lý chính (Redis/RAM)     
    reply  = process_chat_message(request.session_id, request.message)

    # 2. Ném task lưu SQL cho hệ thống chạy ngầm
    background_tasks.add_task(save_to_sql_background,
                              request.session_id,
                              request.message,
                              reply)
    
    # 3. Trả về cho Frontend
    return ChatResponse(reply= reply)

# ENDPOINT 2: THÊM SẢN PHẨM MỚI
@router.post("/add_product",response_model= ProductResponse)
async def create_product(product: ProductCreate,background_tasks: BackgroundTasks):
    try:
        with get_db_connection() as conn:
            # Lệnh SQL Insert vào bảng products
            query = text("""
                INSERT INTO products (name, price, category, description, status)
                OUTPUT INSERTED.product_id  -- Lấy luôn cái ID vừa được tạo
                VALUES (:name, :price, :category, :description, :status)
            """)
            result = conn.execute(query, {
                "name": product.name,
                "price": product.price,
                "category": product.category,
                "description": product.description,
                "status": product.status
            })
            # Lấy ra ID của sản phẩm vừa thêm
            new_product_id = result.scalar()
            conn.commit()

            # Quăng việc đồng bộ sang VectorDB cho background_tasks chạy ngầm
            background_tasks.add_task(sync_products_to_vector_db)
            
            return ProductResponse(
                message="Thêm sản phẩm thành công vào SQL Server",
                product_id= new_product_id
            )
    except Exception as e: 
        print(f"Lỗi khi thêm sản phẩm: {e}")
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi thêm sản phẩm")