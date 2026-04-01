"""
PHASE 4.1: PERSISTENT MEMORY 
Lưu trữ toàn bộ lịch sử hội thoại của khách hàng thẳng vào SQL Server.
Tự động đẻ ra bảng 'chat_history' nếu chưa có.
"""

from langchain_community.chat_message_histories import SQLChatMessageHistory
from src.core.config import settings

def get_chat_memory(session_id: str) -> SQLChatMessageHistory:
    """
    Khởi tạo hoặc gọi lại bộ nhớ dựa trên session_id (Mã phiên chat của user).
    """
    return SQLChatMessageHistory(
        session_id = session_id,
        connection_string= settings.SQL_DATABASE_URL,
        table_name="chat_history" # Bảng này SQLAlchemy sẽ tự đẻ ra trong DB nếu chưa có
    )




