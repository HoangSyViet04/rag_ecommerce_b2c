"""
PHASE 4.3: LLM GENERATOR
Khởi tạo mô hình ngôn ngữ lớn (Gemini) dùng chung cho toàn bộ Router và Agent.
"""

import os
# from langchain_google_genai import ChatGoogleGenerativeAI
from src.core.config import settings
from langchain_community.chat_models import ChatOllama

def get_llm():
    llm = ChatOllama(
        # model= "models/gemini-2.0-flash-lite-001",
        # google_api_key= settings.GEMINI_API_KEY,
        model="qwen2.5",
        temperature=0.2  
        )
    return llm 


