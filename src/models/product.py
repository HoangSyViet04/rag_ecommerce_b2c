from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Product(BaseModel):
    """
    Domain Model ánh xạ 1-1 với schema bảng [products] trong SQL Server.
    Sử dụng Pydantic để validate dữ liệu chặt chẽ ở tầng API và LLM Tool.
    """
    product_id : Optional[int] = Field(default=None, description="Mã sản phẩm, tự động tăng trong DB(Identity)")
    name: str = Field(...,max_length = 255 ,description = "Tên sản phẩm, không được để trống")
    description : Optional[str] = Field(default=None, description="Mô tả sản phẩm chi tiet")
    category : Optional[str] = Field(default=None, max_length=100, description="Danh mục sản phẩm")
    price: float = Field(default=0.0, ge=0, description="Giá (phải >= 0)")
    status : str = Field(default="active", description="Trạng thái sản phẩm (active/inactive)", pattern="^(active|inactive)$")
    updated_at : Optional[datetime] = Field(default=None, description="Thời điểm cập nhật cuối cùng")

    # Config này giúp Pydantic hiểu được object trả về từ SQLAlchemy (ORM mode)
    model_config = {
        "from_attributes": True
    }
                         