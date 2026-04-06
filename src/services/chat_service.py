"""
TẦNG DỊCH VỤ (CHAT SERVICE) - BẢN ENTERPRISE (REDIS + FAIL-SAFE)
Nơi điều phối luồng chạy: Nhận Request -> Rút Memory -> Gọi Não -> Cầm Khiên -> Lưu Memory -> Trả Response
"""
import json
import redis
from src.engine.router import process_query
from src.engine.guardrails import apply_guardrails
from src.core.config import settings

# CẤU HÌNH REDIS / RAM FALLBACK
fallback_memory ={}
USE_REDIS = False
SESSION_TTL = 86400  # Thời gian sống của phiên chat: 24h (tính bằng giây)

try: 
    # Kết nối thẳng vào Redis Server 
    redis_client = redis.Redis(host=settings.REDIS_HOST, 
                               port= settings.REDIS_PORT,
                               db =settings.REDIS_DB,
                               decode_responses= True)
    redis_client.ping() # Kiểm tra kết nối
    USE_REDIS = True
    print(f"-> Kết nối Redis Server thành công")
except redis.ConnectionError:
    print("[X] :Không tìm thấy Redis Server, Hệ thống tự động chuyển sang dùng RAM (Dictionary) để tạm thay thế")

# HÀM XỬ LÝ NGHIỆP VỤ LÕI
def process_chat_message(session_id: str, user_message:str) -> str:
    """Hàm điều phối luồng xử lý tin nhắn của khách hàng"""
    print(f"-> Nhận tin nhắn từ khách hàng:{session_id} : {user_message}")

    chat_history = []
    memory_key = f"chat_history:{session_id}"

    # 1. LẤY LỊCH SỬ CHAT (Từ Redis hoặc RAM)
    if USE_REDIS:
        history_data = redis_client.get(memory_key)
        if history_data:
            chat_history = json.loads(history_data)
            print(f"-> Lấy lịch sử chat từ Redis: {len(chat_history)} tin nhắn")
        else:
            print(f"Tạo phiên chat mới trên Redis cho: {session_id}")
    else:
        chat_history = fallback_memory.get(session_id,[])
        if chat_history:
            print(f"Lấy lịch sử chat từ RAM: {len(chat_history)} tin nhắn")
        else:
            print(f"Tạo phiên chat mới trên RAM cho: {session_id}")

    # 2. GỌI BỘ NÃO AI (Phase 4 - Router)
    try: 
        formatted_history = ""
        if chat_history:
            formatted_history = "\n".join(
                [f"{'Khách' if msg['role']=='user' else 'assistant'}: {msg['content']}" for msg in chat_history[-4:]]
            )
        raw_ai_response = process_query(user_message,chat_history = formatted_history)
    except Exception as e:
        print(f"[Lỗi engine] Sự cố nội bộ:{str(e)}")
        raw_ai_response = "Dạ, hệ thống của em đang bảo trì một chút, anh/chị vui lòng thử lại sau vài giây nhé"

    # 3. GỌI LỚP KHIÊN BẢO VỆ  - Guardrails
    safe_response = apply_guardrails(raw_ai_response)

    # 4. LƯU LỊCH SỬ CHAT MỚI (Vào Redis hoặc RAM)
    chat_history.append({
        "role":"user",
        "content":user_message
    })
    chat_history.append({
        "role":"bot",
        "content": safe_response
    })

    if USE_REDIS:
        redis_client.setex(
            name= memory_key,
            time= SESSION_TTL,
            value= json.dumps(chat_history, ensure_ascii=False)
        )
    else:
        fallback_memory[session_id] = chat_history
        print(f" [SERVICE] Trả kết quả cho '{session_id}': {safe_response}")
    return safe_response




