"""
BỘ LỌC GUARDRAILS: Kiểm duyệt đầu ra của AI trước khi gửi cho khách hàng để ngăn chặn khủng hoảng truyền thông và
rủi ro kinh doanh.
"""


import re

from sqlalchemy import text

# Danh sách đen (Blacklist)
COMPETITORS = ["shopee", "lazada", "tiki", "thế giới di động", "fpt shop", "cellphones", "tiktok shop"]
PROFANITY = ["đm", "vcl", "ngu", "chó", "mẹ mày", "cút"] # Thêm các từ tục tĩu phổ biến trong tiếng Việt

def check_competitors(text: str)-> bool:
    """Kiểm tra xem AI có lỡ mồm nhắc đến đối thủ không."""
    text_lower = text.lower()
    for comp in COMPETITORS:
        if comp in text_lower:
            return True
    return False

def check_profanity(text: str) -> bool:
    """Kiểm tra từ ngữ thô tục."""
    text_lower = text.lower()
    for prof in PROFANITY:
        if prof in text_lower:
            return True
    return False

def check_price_anomaly(text: str) -> bool:
    """
    Kiểm tra lỗi báo giá ảo (Báo giá 0 VNĐ hoặc giá âm).
    AI đôi khi bị ảo giác sẽ sinh ra câu: "Sản phẩm này có giá 0 VNĐ"
    """

    # Tìm tất cả các con số đứng trước chữ "VNĐ", "VND", "đ"
    prices = re.findall(r'(\d+[\d\.,]*)\s*(?:vnđ|vnd|đ)', text.lower())
    for price_str in prices:
        # Xóa dấu chấm/phẩy để ép về số nguyên
        clean_price = re.sub(r'[\.,]','',price_str)
        try:
            if int(clean_price) <=0:
                return True
        except ValueError:
            continue
    return False


def apply_guardrails(ai_response :str) -> str:
    """
    Hàm tổng chạy qua tất cả các lớp khiên.
    Trả về câu trả lời an toàn nếu vi phạm, hoặc trả về nguyên bản nếu pass.
    """
    if check_profanity(ai_response):
        print(f"[guardrail] Đã chặn: Phát hiện từ ngữ nhạy cảm.")
        return "Dạ, em xin phép không trả lời câu hỏi này ạ. Anh/chị có thể hỏi về sản phẩm hoặc dịch vụ khác không ạ?"
    if check_competitors(ai_response):
        print("[guardrail] Đã chặn: Phát hiện tên đối thủ.")
        return "Dạ, hiện tại em chỉ hỗ trợ tư vấn các sản phẩm thuộc hệ thống Store thôi ạ. Anh/chị thông cảm nhé!"
    if check_price_anomaly(ai_response):
        print("[guardrail] Đã chặn: Phát hiện báo giá ảo/ lỗi giá.")
        return "Dạ hệ thống đang cập nhật lại giá sản phẩm này. Anh/chị vui lòng liên hệ trực tiếp nhân viên hoặc chờ trong giây lát nhé!"
    
    return ai_response