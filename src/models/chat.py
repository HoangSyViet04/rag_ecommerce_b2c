from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    """Schema cho Request từ Frontend gửi xuống API"""
    session_id : str = Field(..., description="Mã phiên chat để AI nhớ ngữ cảnh")
    message : str = Field(..., description= "Tin nhắn của khách hàng")

class ChatResponse(BaseModel):
    """Schema cho Response từ API trả về Frontend"""
    reply: str=Field(..., description="Câu trả lời đã được lọc qua Guardrails của AI")
    handoff_flag: bool=Field(default=False, description="Cờ: True nếu bot không hiểu và cần chuyển cho nhân viên")
    recommended_products: List[str] = Field(default=[], description="Danh sách Mã SP (ID) để UI hiển thị chốt sale")

class AgentLLMOutput(BaseModel):
    """Schema nội bộ ép con AI (Gemini) phải trả về đúng chuẩn JSON này"""
    thought_process: str=Field(..., description="Suy nghĩ nội tâm của AI trước khi trả lời")
    final_answer: str=Field(..., description="Câu trả lời cuối cùng cho khách")
    needs_human: bool = Field(default= False, description="Đánh giá xem có cần con người can thiệp không")