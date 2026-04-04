"""
PHASE 4.1 & 5.3: PERSISTENT MEMORY 
build hàm lưu lịch sử chat thẳng vào SQL Server 
"""

from sqlalchemy import text
from src.database.relational_db import get_db_connection

def save_chat_to_sql(session_id: str, sender_role:str,content:str):
    """
    Hàm lưu chat vào SQL Server
    session_id: ID của phiên chat (dùng để phân biệt các cuộc hội thoại khác nhau)
    sender_role: "user" hoặc "bot" để phân biệt người gửi tin nhắn
    content: Nội dung tin nhắn cần lưu
    """
    try:
        with get_db_connection() as conn:
            query = text(""" INSERT INTO ChatHistory(SessionID, SenderRole, Content)
                         VALUES(:session_id,:sender_role,:content) """)
            conn.execute(query,{
                "session_id": session_id,
                "sender_role": sender_role,
                "content": content
            })
            conn.commit()
            print(f"-> Đã lưu lịch sử chat vào SQLServer")
    except Exception as e: 
        print(f"-> Lỗi khi lưu chat vào SQL Server: {e}")