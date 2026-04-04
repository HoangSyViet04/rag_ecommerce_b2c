rag-ecommerce-assistant/
├── data/                       # Dữ liệu tĩnh, DB cục bộ (chroma_db)
├── docs/                       # Sơ đồ kiến trúc, API Docs
├── frontend/                   # Streamlit Web UI
│   └── app.py                  
├── src/                        # Toàn bộ Source Code Backend
│   ├── core/                   # Cấu hình chung
│   │   ├── config.py           # Load .env (LangSmith keys, DB urls...)
│   │   └── exceptions.py       # Xử lý lỗi tập trung
│   ├── models/                 # (UPDATE 1) Domain Models (Dùng chung toàn app)
│   │   ├── product.py          # Class Product
│   │   ├── chat.py             # Class ChatSession, Message
│   │   └── llm_schemas.py      # Định nghĩa output cho LLM (Structured Output)
│   ├── api/                    # Giao tiếp HTTP (FastAPI)
│   │   ├── routes.py           
│   │   └── schemas.py          # DTOs (API Input/Output)
│   ├── database/               # Kết nối 2 Bán cầu não (Dual-DB)
│   │   ├── vector_db.py        # LangChain Chroma Client
│   │   └── relational_db.py    # SQLAlchemy (SQL Server)
│   ├── engine/                 # "Trái tim RAG LangChain"
│   │   ├── memory.py           # (UPDATE 2) 
│   │   ├── retriever.py        # Kỹ thuật truy xuất nâng cao
│   │   ├── router.py           # LCEL RunnableBranch phân luồng
│   │   └── generator.py        # Prompt Templates & Gọi LLM (Gemini)
│   ├── tools/                  # (UPDATE 3) Nơi chứa "vũ khí" cho Agent
│   │   ├── check_stock.py      # Tool check tồn kho
│   │   └── check_price.py      # Tool check giá
│   ├── services/               # Logic nghiệp vụ (Business Logic)
│   │   └── chat_service.py     # Gọi LCEL Pipeline + Tools + Memory
│   ├── processing/
│   │   ├── sync_handler.py        ĐỒNG BỘ DỮ LIỆU SQL -> VECTOR DB
│   │   └── langchain_ingestion.py 
│   │
│   └── utils/                  # Helpers
├── monitoring/                 # LLMOps
│   └── langsmith_tracer.py     # (UPDATE 4) Config LangSmith thay vì CSV
├── tests/                      # Unit/Integration tests
├── .env                        
├── requirements.txt            
└── main.py                     # Entry point FastAPI



🗺️ KẾ HOẠCH TRIỂN KHAI END-TO-END (VER 3.0)
Chúng ta sẽ chia dự án này thành 6 Giai đoạn (Phases). Code xong phase nào, test chạy ngon lành phase đó rồi mới đi tiếp. Nguyên tắc là: Làm từ móng lên tới mái.

📋 KẾ HOẠCH TRIỂN KHAI END-TO-END (ROADMAP CHI TIẾT)
Dự án này sẽ được chia làm 6 Phase (Giai đoạn). Tích hợp thẳng các góp ý của m vào đúng vị trí để code một mạch không bị vấp.

🧱 Phase 1: Khởi tạo & Định nghĩa Domain (Domain-Driven Setup)
Xây dựng bộ khung xương vững chắc, định nghĩa rõ ràng các kiểu dữ liệu.

Task 1.1: Setup .env (Gemini, LangSmith, SQL URL, Redis/Postgres URL).
Nhiệm vụ 1.1: Thiết lập .env (Gemini, LangSmith, SQL URL, Redis URL).

Task 1.2: Code src/core/config.py và src/core/exceptions.py.

Task 1.3: Code src/models/. Dùng Pydantic định nghĩa Product, ChatRequest, ChatResponse, và LLMOutput (đảm bảo AI nhả data đúng format).

🧬 Phase 2: Hybrid Data Pipeline & Sync Strategy 🌟 (Điểm nhấn của m)
Xây dựng ống nạp dữ liệu và cơ chế giữ cho não bộ AI luôn update theo SQL.

Task 2.1 - Ingestion: Code src/processing/langchain_ingestion.py. Cắt văn bản bằng SemanticChunker, nạp vào ChromaDB. Đồng thời build một index BM25 (dùng file json/pickle) lưu song song với Chroma.

Task 2.2 - Sync Logic: Code src/processing/sync_handler.py. Viết một hàm (có thể gọi qua cronjob hoặc API endpoint) để quét SQL Server: "Sản phẩm nào vừa đổi giá? -> Chạy lệnh update metadata price trong ChromaDB ngay lập tức".

⚔️ Phase 3: Cơ sở dữ liệu & Chế tạo vũ khí (DB & Tools)
Mở kết nối DB và trang bị đồ chơi cho Agent.

Task 3.1: Code src/database/vector_db.py và src/database/relational_db.py.

Task 3.2: Code src/tools/. Tạo check_stock, check_price, get_promotions bọc bằng @tool của LangChain. Test độc lập từng tool.

🧠 Phase 4: Trái tim LCEL (The Advanced Engine) 🌟 (Điểm nhấn của m)
Phần cốt lõi khó nhất, ghép nối tư duy của AI.

Task 4.1 - Memory: Code src/engine/memory.py dùng PostgresChatMessageHistory lưu hội thoại vĩnh viễn.

Task 4.2 - Hybrid Retriever: Code src/engine/retriever.py. Dùng EnsembleRetriever kết hợp sức mạnh của BM25Retriever (từ khóa) và Chroma (ngữ nghĩa) với tỷ lệ 0.4 - 0.6.

Task 4.3 - Router & Handoff: Code src/engine/router.py. Phân ra các luồng: RAG thường, Agent (Tools), Chitchat. Thêm logic nhận diện ý định cãi nhau/gặp nhân viên để đẩy vào luồng Human Handoff.

🛡️ Phase 5: Nghiệp vụ & Lớp khiên bảo vệ (Services & Guardrails) 🌟 (Điểm nhấn của m)
Gói bộ não lại, kiểm duyệt đầu ra.

Task 5.1 - Guardrails: Code src/engine/guardrails.py. Viết Regex hoặc dùng 1 LLM nhỏ xíu để check: Có nói giá 0đ không? Có nói bậy không? Có recommend mua web khác không? Nếu vi phạm -> Trả về câu xin lỗi an toàn.
(Chặn đứng rủi ro: Đã xây dựng thành công guardrails.py để làm "bảo vệ cửa". Hệ thống giờ đây miễn nhiễm với việc khách hàng nhắc đến đối thủ (Shopee, Lazada...), chửi thề, hoặc hỏi những câu ngáo giá.
Xử lý tinh tế: Thay vì báo lỗi sập hệ thống, AI tự động tráo bằng các câu trả lời xin lỗi chuẩn nghiệp vụ chăm sóc khách hàng.)

Task 5.2 - Chat Service: Code src/services/chat_service.py nối LCEL chain. Nhận request -> Nạp Memory -> Gọi Router -> Sinh text -> Lọc qua Guardrails -> Trả kết quả.
(Kiến trúc Trí nhớ Kép (Dual-Memory): Đây là điểm "ăn tiền" nhất của hệ thống.
Siêu tốc độ: Dùng bộ nhớ tạm (Redis/RAM) để nhồi ngữ cảnh cho AI, giúp tốc độ phản hồi API nhanh như điện, khách không bị giật lag.
Lưu vết vĩnh viễn: Đã tự code hàm save_chat_to_sql chọc thẳng vào SQL Server lưu dưới dạng văn bản thuần (NVARCHAR). Cột SenderRole lưu chuẩn "user" và "assistant". Admin mở Database ra đọc Tiếng Việt trong vắt, không bị mã hóa lằng nhằng.)

Task 5.3: Mở src/api/routes.py (FastAPI)., them endpoint add_product vào database (Tận dụng Pydantic Schemas: Sử dụng triệt để bộ khuôn đúc xịn xò của ông (models/chat.py và models/product.py) để kiểm duyệt dữ liệu đầu vào tự động (chặn ngay mớ data rác trước khi chạm vào Database).

API /chatbot: Xử lý chat mượt mà. Đã áp dụng Background Tasks để việc lưu log SQL Server chạy ngầm, không làm khách hàng phải chờ đợi.

API /add_product: Cổng cho Admin đăng bán hàng. Tự động lấy product_id sinh ra từ SQL Server, và đỉnh cao nhất là tích hợp Background Task gọi sync_products_to_vector_db để tự động nhét sản phẩm mới vào Não AI (ChromaDB) mà không làm sập luồng chính.)

💻 Phase 6: Giao diện, MLOps & Deploy (UI & Monitoring)
Đưa ra ánh sáng cho khách hàng xài và theo dõi.

Task 6.1: Bật LangSmith tại monitoring/langsmith_tracer.py.

Task 6.2: Code frontend/app.py (Streamlit). Cập nhật UI: Nếu API trả về cờ "HANDOFF", lập tức render một nút to đùng "📞 Gặp Tư vấn viên thật" lên màn hình.

Task 6.3: Viết docker-compose.yml để đóng gói toàn bộ Frontend, Backend, Redis, SQL chạy chung 1 nút bấm.