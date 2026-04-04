"""
Mở cổng Uvicorn, cấu hình CORS chống hack, và gộp các Routes lại.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router

# Khởi tạo App FastAPI
app = FastAPI(
    title="Store RAG E-commerce API",
    description="Hệ thống RAG cho cửa hàng thương mại điện tử - hỗ trợ RAG và Agent.",
    version="1.0.0"
)

# Cấu hình CORS (Vô cùng quan trọng)
# Cho phép Frontend (React/Vue/Mobile) ở các tên miền khác được phép gọi vào API này
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Trong Production, phải đổi "*" thành domain thật của web ông (VD: "https://ai-store.vn")
    allow_credentials=True,
    allow_methods=["*"], # Cho phép mọi method GET, POST, PUT...
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

# Đường dẫn Server
@app.get("/")
def health_check():
    return {"status": "Khởi động ok, M chát được rồi đó."}


# uvicorn src.api.main:app --reload