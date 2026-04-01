from fastapi import HTTPException, status

class DatabaseConnectionError(HTTPException):
    def __init__(self, detail: str = "Không thể kết nối đến SQL server"):
        super().__init__(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail= detail)

class LLMProcessingError(HTTPException):
    def __init__(self, detail: str ="Lỗi khi xử lý với LLM"):
        super().__init__(status_code = status.HTTP_503_SERVICE_UNAVAILABLE, detail= detail)

class ProductNotFoundError(HTTPException):
    def __init__(self, detail : str = "Không tìm thấy sản phẩm"):
        super().__init__(status_code = status.HTTP_404_NOT_FOUND, detail= detail)