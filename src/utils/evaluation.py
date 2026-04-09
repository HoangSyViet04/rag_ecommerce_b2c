import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision
)
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import HuggingFaceEmbeddings

def run_evaluation():
    print("-> Đang nạp đề thi...")
    
    # 1. Chuẩn bị dữ liệu test 
    # Cấu trúc bắt buộc: question, answer (bot trả lời), contexts (tài liệu nhặt được), ground_truth (đáp án chuẩn để so sánh)
    data = {
        "question": [
            "shop có bán tai nghe Sony không?",
            "chính sách bảo hành điện thoại thế nào?"
        ],
        "answer": [
            "Dạ hiện tại AI-Store chưa kinh doanh mặt hàng tai nghe Sony ạ. Bạn có muốn tham khảo các mẫu khác không?",
            "Dạ bảo hành chính hãng 12 tháng tại các trung tâm ủy quyền và lỗi 1 đổi 1 trong 30 ngày đầu ạ."
        ],
        "contexts": [
            ["Cảnh báo: Không tìm thấy sản phẩm nào khớp với yêu cầu."],
            ["Chính sách bảo hành điện thoại: Bảo hành chính hãng 12 tháng tại các trung tâm bảo hành ủy quyền. Lỗi 1 đổi 1 trong 30 ngày đầu nếu có lỗi phần cứng từ nhà sản xuất."]
        ],
        "ground_truth": [
            "Shop không bán tai nghe Sony.",
            "Điện thoại được bảo hành 12 tháng chính hãng và 1 đổi 1 trong 30 ngày."
        ]
    }
    
    dataset = Dataset.from_dict(data)

    # 2. Dùng chính Qwen2.5 và model Embedding BKAI
    print("-> Khởi tạo Ollama...")
    evaluator_llm = ChatOllama(model="qwen2.5", temperature=0.2)
    evaluator_embeddings = HuggingFaceEmbeddings(
        model_name="bkai-foundation-models/vietnamese-bi-encoder",
        encode_kwargs={'normalize_embeddings': True}
    )

    # 3. Chạy đánh giá
    print("-> Đang chấm điểm... ")
    result = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_precision],
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
    )

    # 4. In kết quả
    print("\n=== KẾT QUẢ ĐÁNH GIÁ HỆ THỐNG RAG ===")
    df = result.to_pandas()
    
    print("Các cột hiện có:", df.columns.tolist())
    print("-" * 50)
    print(df.to_string())

if __name__ == "__main__":
    run_evaluation()