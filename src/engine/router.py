"""
PHASE 4.4: INTENT ROUTER (BỘ ĐỊNH TUYẾN NGỮ NGHĨA)
Phân loại ý định của user và rẽ nhánh luồng xử lý chuẩn LCEL.
"""

from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.agents import AgentExecutor, create_react_agent

from src.engine.generator import get_llm
from src.engine.retriever import get_hybrid_retriever
from src.tools.product_tools import ecommerce_tools

llm = get_llm()

# ==========================================
# 1. BỘ PHÂN LOẠI Ý ĐỊNH (CLASSIFIER)
# ==========================================
classifier_template = """Bạn là bộ định tuyến AI của cửa hàng.
Nhiệm vụ: Phân loại câu hỏi của khách hàng vào CHÍNH XÁC 1 trong 4 nhóm sau. Chỉ in ra từ khóa, KHÔNG GIẢI THÍCH.
- 'policy': Khách hỏi về bảo hành, đổi trả, quy định, luật lệ, giao hàng.
- 'product': Khách hỏi giá cả, tồn kho, thông số, tìm kiếm sản phẩm.
- 'handoff': Khách tức giận, khiếu nại, dùng từ ngữ tiêu cực, đòi gặp người thật.
- 'chitchat': Khách chào hỏi, hỏi thăm sức khỏe, hoặc các câu không liên quan bán hàng.

Câu hỏi: {question}
Từ khóa:"""
classifier_chain = ChatPromptTemplate.from_template(classifier_template) | llm | StrOutputParser()

# ==========================================
# 2. XÂY DỰNG CÁC LUỒNG XỬ LÝ (SUB-CHAINS)
# ==========================================

# Luồng A: RAG Chain (Dành cho Policy)
rag_prompt = ChatPromptTemplate.from_template("""Bạn là nhân viên CSKH của AI-Store.
Dựa vào tài liệu quy định sau đây để trả lời khách hàng. Nếu tài liệu không có, hãy nói không biết, đừng bịa ra.
Tài liệu:
{context}

Câu hỏi: {question}
Trả lời lịch sự:""")

rag_chain = (
    {
        "context": itemgetter("question") | get_hybrid_retriever(), 
        "question": itemgetter("question")
    }
    | rag_prompt
    | llm
    | StrOutputParser()
)

# Luồng B: Agent Chain (Dành cho Product/SQL)
agent_prompt = PromptTemplate.from_template("""Bạn là nhân viên bán hàng của AI-Store. 
Bạn có quyền sử dụng các công cụ sau để tra cứu CSDL:

{tools}

Bạn BẮT BUỘC phải tư duy và trả lời theo ĐÚNG định dạng sau (bằng tiếng Việt):

Question: câu hỏi của khách hàng
Thought: Bạn nên nghĩ về việc phải làm gì tiếp theo
Action: hành động bạn chọn, PHẢI LÀ MỘT TRONG CÁC TÊN SAU: [{tool_names}]
Action Input: đầu vào cho hành động đó (ví dụ: tên sản phẩm hoặc danh mục)
Observation: kết quả từ CSDL
... (Quá trình Thought/Action/Action Input/Observation có thể lặp lại nhiều lần nếu cần)
Thought: Tôi đã có đủ thông tin để trả lời khách.
Final Answer: Câu trả lời cuối cùng gửi cho khách (Lịch sự, báo giá VNĐ rõ ràng).

Bắt đầu!

Question: {question}
Thought:{agent_scratchpad}""")

agent = create_react_agent(llm, ecommerce_tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=ecommerce_tools, verbose=True, handle_parsing_errors=True)

def run_agent(question: str) -> str:
    result = agent_executor.invoke({"question": question})
    return result["output"]

# Luồng C: Chitchat Chain
chitchat_prompt = ChatPromptTemplate.from_template("Bạn là nhân viên dễ thương của AI-Store. Khách nói: '{question}'. Hãy trả lời ngắn gọn, thân thiện.")
chitchat_chain = chitchat_prompt | llm | StrOutputParser()

# Luồng D: Human Handoff (Lối thoát hiểm)
def run_handoff(question: str) -> str:
    return "Dạ em nhận thấy sự bất tiện của anh/chị. Em xin phép kết nối anh/chị với nhân viên hỗ trợ trực tiếp ngay bây giờ ạ!"



# 3. LẮP RÁP CÁC LUỒNG 
def route_logic(info: dict) -> str:
    intent = info["intent"].strip().lower()
    question = info["question"]
    
    print(f"\n Đã bắt được ý định: {intent.upper()}")
    
    if "policy" in intent:
        # Truyền đúng chuẩn dict vào rag_chain để itemgetter hoạt động
        return rag_chain.invoke({"question": question})
    elif "product" in intent:
        return run_agent(question)
    elif "handoff" in intent:
        return run_handoff(question)
    else:
        return chitchat_chain.invoke({"question": question})

master_chain = (
    {"intent": classifier_chain, "question": RunnablePassthrough()}
    | RunnableLambda(route_logic)
)

def process_query(question: str) -> str:
    return master_chain.invoke(question)