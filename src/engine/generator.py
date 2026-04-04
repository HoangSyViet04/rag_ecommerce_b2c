"""
PHASE 4.3: LLM GENERATOR
Khởi tạo mô hình ngôn ngữ lớn (Gemini) dùng chung cho toàn bộ Router và Agent.
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from src.core.config import settings

def get_llm():
    """
    Khởi tạo Gemini 2.5 Flash.
    Set temperature = 0.2 để câu trả lời nhất quán, không bị bay bổng quá đà trong E-commerce.
    """

    llm = ChatGoogleGenerativeAI(
        model= "models/gemini-2.5-flash",
        google_api_key= settings.GEMINI_API_KEY,
        temperature=0.2,
        convert_system_message_to_human=True
    )
    return llm 

