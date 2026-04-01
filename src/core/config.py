"""
CẤU HÌNH TẬP TRUNG TOÀN HỆ THỐNG
Tự động nạp và validate dữ liệu từ file .env
"""

import urllib.parse
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field,computed_field

class Settings(BaseSettings):
    """
    Cấu hình tập trung cho toàn hệ thống
    """
    # Thông tin dự án
    PROJECT_NAME: str = "RAG E-Commerce B2C"
    # Ai models
    GEMINI_API_KEY : str = Field(...,description= "Bắt buộc phải có API KEY của Gemini")
    # Cấu hình SQL Server (Đọc từ .env)
    DB_SERVER : str
    DB_DATABASE: str
    DB_USERNAME : str
    DB_PASSWORD :str
    DB_DRIVER : str

    # Cấu hình LangSmith
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "default"

    @computed_field
    def SQL_DATABASE_URL(self) -> str:
        """
        Tự động tạo chuỗi kết nối SQLAlchemy an toàn.
        Sử dụng urllib.parse để mã hóa mật khẩu chứa ký tự đặc biệt (như '@').
        """
        encoded_password = urllib.parse.quote_plus(self.DB_PASSWORD)
        # Thay thế khoảng trắng trong tên Driver thành dấu '+' theo chuẩn URL
        driver_formatted = self.DB_DRIVER.replace(" ","+")

        return f"mssql+pyodbc://{self.DB_USERNAME}:{encoded_password}@{self.DB_SERVER}/{self.DB_DATABASE}?driver={driver_formatted}"
    
    # Load file .env bỏ qua các biến thừa
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding="utf-8",
        extra="ignore"
    )


# khoi tạo instance cấu hình toàn cục
settings = Settings()

