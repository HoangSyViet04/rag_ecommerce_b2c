"""
MLOps & MONITORING : Công tắc kích hoạt LangSmith để theo dõi (trace) toàn bộ luồng suy nghĩ của LLM.
"""

import os
from src.core.config import settings

def enable_langsmith_tracing():
    if settings.LANGCHAIN_TRACING_V2.lower() == "true":
        os.environ["LANGCHAIN_TRACING_V2"] = settings.LANGCHAIN_TRACING_V2
        os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
        print(f"LANGSMITH Tracing đã bật . Project :{settings.LANGCHAIN_PROJECT}")
    else:
        print(f"LangSmith Tracing đang tắt")


if __name__ == "__main__":
    enable_langsmith_tracing()