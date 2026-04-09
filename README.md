# 🛒 B2C E-Commerce RAG System — Trợ Lý Bán Hàng AI Tự Trị

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python" />
  <img src="https://img.shields.io/badge/LangChain-0.2.x-green?logo=langchain" />
  <img src="https://img.shields.io/badge/LLM-Qwen2.5_(Local)-orange?logo=ollama" />
  <img src="https://img.shields.io/badge/Vector_DB-ChromaDB-yellow" />
  <img src="https://img.shields.io/badge/SQL_Server-2025-red?logo=microsoftsqlserver" />
  <img src="https://img.shields.io/badge/Cache-Redis-DC382D?logo=redis" />
  <img src="https://img.shields.io/badge/Deploy-Docker_Compose-2496ED?logo=docker" />
</p>

Hệ thống **RAG (Retrieval-Augmented Generation)** chuyên biệt cho lĩnh vực **thương mại điện tử B2C**. Dự án xây dựng một trợ lý AI có khả năng **tư vấn sản phẩm**, **chốt sale** và **giải đáp chính sách** một cách chính xác, dựa hoàn toàn trên hệ thống cơ sở dữ liệu nội bộ của doanh nghiệp — loại bỏ hoàn toàn tình trạng **"ảo giác" (Hallucination)** của LLM.

> **Không cần API key của OpenAI/Google.** Toàn bộ suy luận chạy local qua Ollama (`Qwen2.5`), zero API cost.

---

## 📑 Mục Lục

- [Điểm Nổi Bật Kỹ Thuật](#-điểm-nổi-bật-kỹ-thuật-key-technical-highlights)
- [Kiến Trúc Hệ Thống](#-kiến-trúc-hệ-thống-system-architecture)
- [Cấu Trúc Thư Mục](#-cấu-trúc-thư-mục-project-structure)
- [Tech Stack](#-tech-stack)
- [Hướng Dẫn Cài Đặt](#-hướng-dẫn-cài-đặt-setup-guide)
- [Cấu Hình Biến Môi Trường](#-cấu-hình-biến-môi-trường-environment-variables)
- [API Endpoints](#-api-endpoints)
- [Chi Tiết Kỹ Thuật Từng Module](#-chi-tiết-kỹ-thuật-từng-module)
- [Đánh Giá & Đo Lường](#-đánh-giá--đo-lường-evaluation)
- [Roadmap Phát Triển](#-roadmap-phát-triển)

---

## 🚀 Điểm Nổi Bật Kỹ Thuật (Key Technical Highlights)

### 1. Kiến Trúc — 100% Local, Zero API Cost
Hệ thống **không phụ thuộc vào bất kỳ API trả phí nào** (OpenAI, Google, Anthropic...). Toàn bộ pipeline AI chạy on-premise:
- **LLM:** `Qwen2.5` chạy qua **Ollama** (`temperature=0.2` cho output ổn định, deterministic).
- **Embedding:** `bkai-foundation-models/vietnamese-bi-encoder` — model tiếng Việt chuyên biệt từ BKAI, áp dụng `normalize_embeddings=True` cho cosine similarity chính xác hơn.
- **Ý nghĩa:** Bảo mật dữ liệu doanh nghiệp tuyệt đối, không có data nào rời khỏi server. Chi phí vận hành = 0đ.

### 2. Intent Router — Phân Luồng Suy Luận 4 Nhánh
Hệ thống tự động phân loại ý định người dùng thành **4 luồng xử lý** riêng biệt, mỗi luồng có chain LCEL tối ưu riêng:

| Ý định (Intent) | Luồng xử lý | Mô tả |
|---|---|---|
| `policy` | **RAG Chain** | Hỏi chính sách đổi trả, bảo hành → Hybrid Retriever (Vector + BM25) |
| `product` | **ReAct Agent** | Hỏi giá, tồn kho, tìm sản phẩm → Agent gọi Tools truy vấn SQL/ChromaDB |
| `handoff` | **Human Handoff** | Phát hiện giọng giận dữ, khiếu nại → Trả cờ `handoff_flag=true` cho Frontend |
| `chitchat` | **Chitchat Chain** | Chào hỏi, tâm sự → Trả lời thân thiện, không query DB |

### 3. Hybrid Database — "Não Bộ Kép"
Kết hợp **2 loại database** để khắc phục điểm yếu của nhau:
- **ChromaDB** (Vector Store): Tìm kiếm **ngữ nghĩa** — khách miêu tả nhu cầu mơ hồ ("tôi cần cái gì đó nghe nhạc hay"), AI vẫn hiểu.
- **SQL Server** (Relational DB): Tìm kiếm **chính xác** — so sánh giá, lọc danh mục, check tồn kho bằng SQL thuần. Khắc phục triệt để điểm yếu toán học của Vector DB.
- **Redis** (Cache Layer): Lưu context hội thoại tạm thời (TTL 24h), tốc độ đọc/ghi < 1ms.

### 4. Hybrid Retriever — BM25 + Semantic Search
Không dùng riêng Vector Search hay BM25, mà **kết hợp cả hai** qua `EnsembleRetriever` của LangChain:
- **Vector Retriever** (trọng số `0.7`): Bắt được các câu hỏi diễn đạt tự nhiên, ngữ nghĩa tương đồng.
- **BM25 Retriever** (trọng số `0.3`): Bắt chính xác các từ khóa cụ thể (tên sản phẩm, mã, số liệu).
- **Kết quả:** Tỷ lệ recall cao hơn đáng kể so với dùng riêng lẻ từng phương pháp.

### 5. Ngăn Chặn Ảo Giác — Guardrails 3 Lớp
Hệ thống **"bảo vệ cửa"** kiểm duyệt mọi output của AI trước khi trả về khách hàng:

| Lớp | Kiểm tra | Xử lý khi vi phạm |
|---|---|---|
| **Profanity Filter** | Từ khóa thô tục (`đm`, `ngu`, `chó`...) | *"Dạ, em xin phép không trả lời nội dung này..."* |
| **Competitor Filter** | Nhắc đối thủ (`Shopee`, `Lazada`, `Tiki`, `TikTok Shop`, `FPT Shop`...) | *"Dạ, em chỉ hỗ trợ sản phẩm của Store..."* |
| **Price Anomaly** | Giá ≤ 0đ — phát hiện ảo giác toán học bằng Regex | *"Dạ hệ thống đang cập nhật giá, vui lòng thử lại..."* |

> Xử lý tinh tế: Thay vì báo lỗi sập hệ thống, AI tự động thay thế bằng các câu trả lời xin lỗi chuẩn nghiệp vụ chăm sóc khách hàng.

### 6. Kiến Trúc Trí Nhớ Kép (Dual-Memory Architecture)
- **Tầng tốc độ (Redis):** Lưu 4 tin nhắn gần nhất vào Redis (TTL 24h). AI đọc ngữ cảnh từ đây để phản hồi nhanh, khách không bị giật lag. Có **fallback tự động sang in-memory dict** nếu Redis chết — hệ thống không bao giờ sập.
- **Tầng lưu trữ vĩnh viễn (SQL Server):** Mọi tin nhắn được ghi vào bảng `ChatHistory` qua **FastAPI Background Task** (chạy ngầm, không block response). Admin mở DB đọc Tiếng Việt rõ ràng (`NVARCHAR`), cột `SenderRole` lưu chuẩn `"user"` / `"bot"`.

### 7. Data Sync Pipeline — SQL ↔ Vector DB Tự Động
Module `sync_handler.py` giữ cho "não AI" luôn đồng bộ với database gốc:
- Quét toàn bộ bảng `products` trong SQL Server.
- Sản phẩm **active** → Upsert vào ChromaDB (idempotent, tự cập nhật nếu đã tồn tại qua ID `prod_{product_id}`).
- Sản phẩm **inactive** → Xóa khỏi ChromaDB ngay lập tức.
- **Trigger tự động:** Gọi qua cronjob (5 phút/lần) hoặc tự động kích hoạt sau mỗi lần Admin thêm sản phẩm mới qua API `/add_product`.

### 8. Đo Lường & Đánh Giá Tự Động (RAG Evaluation)
Tích hợp framework **Ragas** đo lường 3 chỉ số cốt lõi của hệ thống RAG:
- **Faithfulness:** Câu trả lời có bám sát context truy xuất được không? (chống hallucination)
- **Answer Relevancy:** Câu trả lời có thực sự liên quan đến câu hỏi?
- **Context Precision:** Context mà Retriever trả về có chứa thông tin cần thiết?

---

## 🧠 Kiến Trúc Hệ Thống (System Architecture)

<p align="center">
  <img src="docs/architecture.png" alt="System Architecture" width="100%" />
</p>

### Luồng xử lý chi tiết (Request Lifecycle)

1. **Request →** Frontend gửi `POST /api/chatbot` với `{session_id, message}`.
2. **Load Memory →** Chat Service đọc 4 tin nhắn gần nhất từ Redis (fallback: in-memory dict).
3. **Classify →** Intent Router phân loại câu hỏi thành 1 trong 4 luồng (`policy` / `product` / `handoff` / `chitchat`).
4. **Execute →** Tùy luồng:
   - *Policy:* `EnsembleRetriever` (BM25 + Chroma) → RAG Chain → Format answer theo giọng CSKH.
   - *Product:* `ReAct Agent` → Gọi Tools (`check_price`, `search_category`, `semantic_search`) → Truy vấn SQL/ChromaDB → Tổng hợp.
   - *Chitchat:* LLM trả lời thân thiện, không truy vấn DB.
   - *Handoff:* Trả về `handoff_flag=true` → Frontend render nút gọi tư vấn viên.
5. **Filter →** Output đi qua 3 lớp Guardrails (Profanity → Competitor → Price Anomaly).
6. **Save →** Background Task ghi cả `user` + `bot` message vào SQL Server (`ChatHistory`).
7. **Response →** Trả `ChatResponse` về Frontend.

---

## 📁 Cấu Trúc Thư Mục (Project Structure)

```
rag_ecommerce_b2c/
│
├── 📄 main.py                              # Entry point (backup)
├── 📄 requirements.txt                     # Python dependencies
├── 📄 Dockerfile                           # Build Backend image (Python 3.11 + ODBC Driver 17)
├── 📄 docker-compose.yml                   # Orchestrate 5 services (Redis, SQL, Backend, Frontend, DB-Init)
├── 📄 .env                                 # Biến môi trường 
│
├── 📂 data/                                # Dữ liệu tĩnh & DB cục bộ
│   ├── 📄 init.sql                         # Script khởi tạo Database + Tables + Sample data
│   ├── 📂 raw/                             # Tài liệu gốc (.txt, .pdf, .docx) để nạp vào Vector DB
│   │   └── 📄 CHÍNH SÁCH ĐỔI TRẢ...txt   # Văn bản chính sách bảo hành, đổi trả
│   └── 📂 chroma_db/                       # ChromaDB persistent storage (auto-generated)
│       └── 📄 chroma.sqlite3
│
├── 📂 src/                                 # ═══ TOÀN BỘ BACKEND SOURCE CODE ═══
│   │
│   ├── 📂 core/                            #  Cấu hình & Xử lý lỗi tập trung
│   │   ├── 📄 config.py                    # Pydantic Settings: load .env, auto-build SQL_DATABASE_URL
│   │   └── 📄 exceptions.py               # Custom HTTPException (500, 503, 404)
│   │
│   ├── 📂 models/                          #  Domain Models 
│   │   ├── 📄 product.py                   # Product, ProductCreate, ProductResponse
│   │   └── 📄 chat.py                      # ChatRequest, ChatResponse, AgentLLMOutput
│   │
│   ├── 📂 database/                        
│   │   ├── 📄 vector_db.py                 # ChromaDB Singleton + BM25 pickle loader
│   │   └── 📄 relational_db.py             # SQLAlchemy Engine (pool_size=5, pool_pre_ping)
│   │
│   ├── 📂 processing/                      # Data Pipeline & Đồng bộ hóa
│   │   ├── 📄 langchain_ingestion.py       # Multi-format loader → SemanticChunker → Chroma + BM25
│   │   └── 📄 sync_handler.py              # SQL → ChromaDB sync (upsert active, delete inactive)
│   │
│   ├── 📂 engine/                          
│   │   ├── 📄 generator.py                 # LLM factory: ChatOllama(qwen2.5, temp=0.2)
│   │   ├── 📄 retriever.py                 # EnsembleRetriever: Vector(0.7) + BM25(0.3)
│   │   ├── 📄 router.py                    # Intent Classifier → 4 LCEL Chains + ReAct AgentExecutor
│   │   ├── 📄 guardrails.py                # 3-layer filter: Profanity → Competitor → Price Anomaly
│   │   └── 📄 memory.py                    # save_chat_to_sql() — lưu hội thoại vĩnh viễn vào SQL
│   │
│   ├── 📂 tools/                          
│   │   └── 📄 product_tools.py             # 3 @tool: check_price, search_category, semantic_search
│   │
│   ├── 📂 services/                        
│   │   └── 📄 chat_service.py              # Orchestrator: Redis → Router → Guardrails → Response
│   │
│   ├── 📂 api/                             # REST API (FastAPI)
│   │   ├── 📄 main.py                      # App factory, CORS middleware, startup event
│   │   └── 📄 routes.py                    # POST /chatbot + POST /add_product
│   │
│   └── 📂 utils/                           #  Utilities
│       ├── 📄 evaluation.py                # Ragas evaluation (Faithfulness, Relevancy, Precision)
│       └── 📄 inspect_chroma.py            # Debug tool: xem nội dung ChromaDB
│
├── 📂 monitoring/                          #  LLMOps & Observability
│   └── 📄 langsmith_tracer.py              # Enable LangSmith tracing on startup
│
├── 📂 frontend/                            #  Giao diện Chat
│   └── 📄 index.html                       # Chat UI (Vanilla JS) + Handoff button rendering
│
├── 📂 tests/                               
│
└── 📂 docs/                                #  Tài liệu bổ sung
```

---

## 💻 Tech Stack

| Layer | Công nghệ | Vai trò |
|---|---|---|
| **Language** | Python 3.11 | Core runtime |
| **Web Framework** | FastAPI + Uvicorn | REST API, async support, Background Tasks |
| **LLM Orchestration** | LangChain 0.2.x | LCEL chains, ReAct Agent, EnsembleRetriever |
| **Local LLM** | Ollama (`qwen2.5`) | Suy luận, phân loại intent, sinh câu trả lời |
| **Embedding Model** | `bkai-foundation-models/vietnamese-bi-encoder` | Vector hóa văn bản tiếng Việt |
| **Vector Database** | ChromaDB 0.4.x | Semantic search, persistent storage |
| **Keyword Search** | `rank-bm25` (BM25Okapi) | Exact keyword matching, pickle serialized |
| **Relational DB** | SQL Server 2025 + SQLAlchemy ORM | Products, ChatHistory, structured queries |
| **Cache** | Redis (Alpine) | Session memory (TTL 24h), connection pooling |
| **Data Validation** | Pydantic v2 | Request/Response schemas, Settings management |
| **Document Loaders** | LangChain (`TextLoader`, `PyPDFLoader`, `Docx2txtLoader`) | Multi-format document ingestion |
| **Text Splitting** | `SemanticChunker` (standard_deviation) | Cắt chunk thông minh theo ngữ nghĩa |
| **Evaluation** | Ragas | Faithfulness, Answer Relevancy, Context Precision |
| **Monitoring** | LangSmith | Tracing toàn bộ LLM calls & chain execution |
| **Frontend** | Vanilla HTML/CSS/JS + Nginx | Chat UI, Handoff button |
| **Containerization** | Docker + Docker Compose | 5 services, 1-click deploy |

---

## 🛠️ Hướng Dẫn Cài Đặt (Setup Guide)

### Yêu Cầu Hệ Thống

- **Python** 3.11+
- **Ollama** đã cài và pull model: `ollama pull qwen2.5`
- **SQL Server** 2019+ (hoặc dùng Docker)
- **Redis** (hoặc dùng Docker)
- **ODBC Driver 17 for SQL Server** (nếu chạy local, không cần nếu dùng Docker)

---

### Cách 1: Chạy Local (Development)

```bash
# 1. Clone dự án
git clone https://github.com/your-username/rag_ecommerce_b2c.git
cd rag_ecommerce_b2c

# 2. Tạo môi trường ảo
python -m venv venv

# 3. Kích hoạt venv
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# macOS / Linux:
source venv/bin/activate

# 4. Cài đặt dependencies
pip install -r requirements.txt

# 5. Tạo file .env (xem mục "Cấu Hình Biến Môi Trường" bên dưới)
# Copy từ .env.example hoặc tạo mới theo hướng dẫn

# 6. Khởi động Ollama (mở terminal riêng)
ollama serve
# Pull model nếu chưa có:
ollama pull qwen2.5

# 7. Nạp dữ liệu vào ChromaDB + BM25 index (chạy 1 lần đầu)
python -c "from src.processing.langchain_ingestion import run_hybrid_ingestion; run_hybrid_ingestion()"

# 8. Khởi động FastAPI server
uvicorn src.api.main:app --reload --port 8000
```

> **Truy cập:**
> - Health check: http://localhost:8000
> - Swagger UI (API docs): http://localhost:8000/docs
> - Chat UI: Mở `frontend/index.html` trực tiếp trong trình duyệt

---

### Cách 2: Docker Compose (Production — 1 Click Deploy)

```bash
# 1. Clone dự án
git clone https://github.com/your-username/rag_ecommerce_b2c.git
cd rag_ecommerce_b2c

# 2. Tạo file .env (bắt buộc - chứa DB_PASSWORD cho SQL Server)
# Xem mục "Cấu Hình Biến Môi Trường" bên dưới

# 3. Build và khởi động toàn bộ hệ thống (5 containers)
docker-compose up -d --build
```

Docker Compose sẽ tự động khởi chạy **5 services**:

| # | Service | Container Name | Port | Mô tả |
|---|---|---|---|---|
| 1 | `redis` | `ai_store_redis` | `6379` | Cache session memory (Alpine, nhẹ) |
| 2 | `sqlserver` | `ai_store_sql` | `1433` | Database chính — Products + ChatHistory |
| 3 | `db-init` | `ai_store_db_init` | — | Chạy `init.sql` tạo DB/Tables/Sample data, rồi tự tắt |
| 4 | `backend` | `ai_store_backend` | `8000` | FastAPI + AI Engine (Python 3.11 + ODBC Driver 17) |
| 5 | `frontend` | `ai_store_frontend` | `80` | Nginx serve giao diện Chat |


```bash
# Xem logs real-time
docker-compose logs -f backend

# Dừng hệ thống (giữ data)
docker-compose down

# Dừng và xóa toàn bộ data (volumes)
docker-compose down -v
```

> **Truy cập sau khi deploy:**
> - Chat UI: http://localhost (port 80)
> - API Backend: http://localhost:8000
> - Swagger Docs: http://localhost:8000/docs

---

## 🔑 Cấu Hình Biến Môi Trường (Environment Variables)

Tạo file `.env` tại thư mục gốc dự án:

```env
# ╔══════════════════════════════════════════╗
# ║     CẤU HÌNH HỆ THỐNG RAG E-COMMERCE    ║
# ╚══════════════════════════════════════════╝

# === SQL Server ===
DB_SERVER=localhost              # → "sqlserver" nếu chạy Docker Compose
DB_DATABASE=RagB2C_Inventory
DB_USERNAME=sa
DB_PASSWORD=YourStrongPassword123!
DB_DRIVER=ODBC Driver 17 for SQL Server

# === Redis ===
REDIS_HOST=localhost             # → "redis" nếu chạy Docker Compose
REDIS_PORT=6379
REDIS_DB=0

# === LangSmith Monitoring (Optional) ===
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=ls_xxxxxxxxxxxxxxxx
LANGCHAIN_PROJECT=rag-ecommerce-b2c

# === Misc ===
ANONYMIZED_TELEMETRY=false
```
---

## 📡 API Endpoints

### `POST /api/chatbot` — Chat với AI Assistant

**Request Body:**
```json
{
  "session_id": "session_abc123",
  "message": "Shop có bán tai nghe Sony không?"
}
```

**Response (200 OK):**
```json
{
  "reply": "Dạ, shop mình hiện có Tai nghe Bluetooth Sony với giá 3.500.000 VNĐ ạ. Sản phẩm đang còn hàng, anh/chị muốn em tư vấn thêm không ạ?",
  "handoff_flag": false,
  "recommended_products": []
}
```

**Luồng xử lý nội bộ:**
1. Load 4 tin nhắn gần nhất từ Redis (`chat_history:{session_id}`)
2. Intent Router classify → `"product"` → Chuyển sang ReAct Agent
3. Agent gọi `check_product_status_and_price("Sony")` → Query SQL Server (`LIKE`)
4. Agent tổng hợp kết quả → Format giá tiền VNĐ → Sinh câu trả lời CSKH
5. Guardrails check 3 lớp 
6. **Background Task:** Lưu cả `user` + `bot` message vào `ChatHistory` (SQL Server)
7. Trả `ChatResponse` về client

---

### `POST /api/add_product` — Thêm sản phẩm mới (Admin)

**Request Body:**
```json
{
  "name": "Loa Bluetooth JBL Flip 6",
  "price": 2890000,
  "category": "dien_tu",
  "description": "Loa di động chống nước IP67, pin 12h, âm bass mạnh mẽ",
  "status": "active"
}
```

**Response (200 OK):**
```json
{
  "message": "Thêm sản phẩm thành công!",
  "product_id": 15
}
```

## 📄 License

MIT License — Free for personal and commercial use.

---

<p align="center">
  <b>Built with ❤️ using LangChain + Ollama + ChromaDB + SQL Server</b>
</p>
