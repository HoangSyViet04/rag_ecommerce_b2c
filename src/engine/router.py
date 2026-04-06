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

# 1. BỘ PHÂN LOẠI Ý ĐỊNH (CLASSIFIER)
classifier_template = """Bạn là bộ định tuyến AI của cửa hàng.
Nhiệm vụ: Phân loại câu hỏi của khách hàng vào CHÍNH XÁC 1 trong 4 nhóm sau. Chỉ in ra từ khóa, KHÔNG GIẢI THÍCH.
- 'policy': Khách hỏi về bảo hành, đổi trả, quy định, luật lệ, giao hàng.
- 'product': Khách hỏi giá cả, tồn kho, thông số, tìm kiếm sản phẩm.
- 'handoff': Khách tức giận, khiếu nại, dùng từ ngữ tiêu cực, đòi gặp người thật.
- 'chitchat': Khách chào hỏi, hỏi thăm sức khỏe, hoặc các câu không liên quan bán hàng.

Câu hỏi: {question}
Từ khóa:"""

classifier_chain = (
    {"question": RunnablePassthrough()} 
    | ChatPromptTemplate.from_template(classifier_template) 
    | llm 
    | StrOutputParser()
)

# 2. XÂY DỰNG CÁC LUỒNG XỬ LÝ (SUB-CHAINS)

# Luồng A: RAG Chain (Dành cho Policy)
rag_prompt = ChatPromptTemplate.from_template("""Bạn là nhân viên Chăm sóc khách hàng tận tâm của AI-Store.
Dựa vào tài liệu quy định sau đây để trả lời khách hàng. 
Yêu cầu tác phong: Luôn xưng hô "Dạ/Vâng", giải thích cặn kẽ, nhẹ nhàng và lịch sự. Nếu tài liệu không có, hãy khéo léo xin lỗi và nói không biết, tuyệt đối không bịa ra thông tin.

Lịch sử trò chuyện gần đây:
{chat_history}

Tài liệu:
{context}

Câu hỏi: {question}
Trả lời lịch sự:""")

rag_chain = (
    {
        "context": itemgetter("question") | get_hybrid_retriever(), 
        "question": itemgetter("question"),
        "chat_history": itemgetter("chat_history") 
    }
    | rag_prompt
    | llm
    | StrOutputParser()
)

# Luồng B: Agent Chain (Dành cho Product/SQL)
agent_prompt = PromptTemplate.from_template("""Bạn là một Chuyên viên tư vấn bán hàng cực kỳ nhiệt huyết và duyên dáng của AI-Store.
Nhiệm vụ của bạn không chỉ là đọc thông tin từ cơ sở dữ liệu, mà phải TƯ VẤN và CHỐT SALE thật mượt mà.

Tác phong BẮT BUỘC trong câu trả lời cuối cùng (Final Answer):
1. Thái độ: Luôn mở đầu bằng "Dạ", xưng hô thân thiện, thể hiện sự niềm nở đón khách.
2. Trình bày: Định dạng giá tiền rõ ràng, dễ đọc (VD: 3.500.000 VNĐ thay vì 3500000).câu văn có cảm xúc, nhưng không lạm dụng.
3. Nội dung: Thay vì copy y nguyên dữ liệu khô khan, hãy dùng lời văn mềm mỏng để khen ngợi sản phẩm, làm nổi bật điểm mạnh.
4. Chốt sale: LUÔN LUÔN kết thúc bằng một câu hỏi gợi mở để níu chân khách.

Bạn có quyền sử dụng các công cụ sau để tra cứu CSDL:

{tools}

Lịch sử trò chuyện gần đây:
{chat_history}

Bạn BẮT BUỘC phải tư duy và trả lời theo ĐÚNG định dạng sau (bằng tiếng Việt):

Question: câu hỏi của khách hàng
Thought: Bạn nên nghĩ về việc phải làm gì tiếp theo
Action: hành động bạn chọn, PHẢI LÀ MỘT TRONG CÁC TÊN SAU: [{tool_names}]
Action Input: đầu vào cho hành động đó
Observation: kết quả từ CSDL
... (Quá trình Thought/Action/Action Input/Observation có thể lặp lại nhiều lần nếu cần)
Thought: Tôi đã tìm thấy sản phẩm, bây giờ tôi sẽ viết một câu tư vấn thật nhiệt tình để chốt sale.
Final Answer: Câu trả lời tư vấn cuối cùng gửi cho khách (Đảm bảo áp dụng đúng 4 quy tắc tác phong ở trên).

Bắt đầu!

Question: {question}
Thought:{agent_scratchpad}""")

agent = create_react_agent(llm, ecommerce_tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=ecommerce_tools, verbose=True, handle_parsing_errors=True)

def run_agent(question: str, chat_history: str) -> str:
    # Truyền thêm lịch sử chat vào Agent
    result = agent_executor.invoke({
        "question": question, 
        "chat_history": chat_history
    })
    return result["output"]

# Luồng C: Chitchat Chain
chitchat_prompt = ChatPromptTemplate.from_template("""Bạn là nhân viên lễ tân vui vẻ, hoạt ngôn của AI-Store. 

Lịch sử trò chuyện:
{chat_history}

Khách nói: '{question}'. 
Hãy trả lời thật tự nhiên, thân thiện, có thể pha chút hài hước nếu phù hợp, luôn xưng hô Dạ/Vâng. Đừng trả lời như một cái máy.""")
chitchat_chain = chitchat_prompt | llm | StrOutputParser()


# Luồng D: Human Handoff (Lối thoát hiểm)
def run_handoff(question: str) -> str:
    return "Dạ em nhận thấy sự bất tiện của anh/chị. Em xin phép kết nối anh/chị với nhân viên hỗ trợ trực tiếp ngay bây giờ ạ!"

# 3. LẮP RÁP CÁC LUỒNG 
def route_logic(info: dict) -> str:
    intent = info["intent"].strip().lower()
    question = info["question"]
    chat_history = info.get("chat_history", "")
    
    print(f"\n Đã bắt được ý định: {intent.upper()}")
    
    if "policy" in intent:
        return rag_chain.invoke({"question": question, "chat_history": chat_history})
    elif "product" in intent:
        return run_agent(question, chat_history)
    elif "handoff" in intent:
        return run_handoff(question)
    else:
        return chitchat_chain.invoke({"question": question, "chat_history": chat_history})

def process_query(question: str, chat_history: str = "") -> str:
    # 1. Phân loại câu hỏi (Chỉ cần question để phân loại cho chuẩn xác)
    intent = classifier_chain.invoke(question)
    
    # 2. Đóng gói dữ liệu ném vào Router
    info = {
        "intent": intent,
        "question": question,
        "chat_history": chat_history
    }
    
    # 3. Rẽ nhánh
    return route_logic(info)