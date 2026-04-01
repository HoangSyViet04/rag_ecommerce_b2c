"""
PHASE 3: QUẢN LÝ KẾT NỐI DATABASE QUAN HỆ (SQL SERVER)
Sử dụng SQLAlchemy Engine với Connection Pooling tối ưu.
"""


from sqlalchemy import create_engine
from src.core.config import settings

# Khởi tạo Engine dùng chung (Singleton) cho toàn app
# pool_pre_ping=True giúp tự động kiểm tra và kết nối lại nếu kết nối tới DB bị rớt

engine  = create_engine(settings.SQL_DATABASE_URL,
                         pool_pre_ping = True,
                         pool_size= 5,          # Số lượng kết nối tối đa trong pool
                        max_overflow= 10,      # Số lượng kết nối tối đa có thể tạo thêm khi pool đã đầy
)


def get_db_connection():
    """
    Hàm cấp phát kết nối an toàn. 
    Dùng chung cho Tools và sau này làm Dependency Injection cho FastAPI.
    """
    return engine.connect()