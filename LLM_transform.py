from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv

class Transform:
    def __init__(self, llm):
        self.llm = llm
        self.memory = ConversationBufferMemory(memory_key="history", input_key="query")
        self.prompt_template = ChatPromptTemplate.from_messages([
            HumanMessagePromptTemplate.from_template(
                """
     Lịch sử truy vấn:
    {history}


    Câu hỏi hiện tại: {query}

    *Quy trình xử lý*:
    Trả về lịch sử truy vấn nhận được dưới dạng :"Lịch sử truy vấn": nội dung
    1. *Kiểm tra ngôn ngữ*:
       - Nếu câu hỏi hiện tại không hoàn toàn bằng tiếng Việt không cần dựa vào lịch sử truy vấn (bao gồm cả các từ đơn lẻ hoặc cụm từ thông dụng không mang ý nghĩa cụ thể trong tiếng Việt như "hi", "hello", "hey"), trả về::
         *Truy vấn chuyển đổi:* "Tôi không hiểu bạn đang nói gì."

    2. *Xác định phạm vi và chuyển đổi câu hỏi*:
       - Nếu câu hỏi liên quan đến Luật Hôn nhân và Gia đình Việt Nam:
         - *Trường hợp câu hỏi có số điều luật, chương, hoặc mục*:
           - Giữ nguyên số điều, chương, hoặc mục đã được đề cập.
           - Chuyển đổi câu hỏi thành dạng đầy đủ và rõ ràng. Ví dụ:
             "Điều [số điều luật]/ Chương [số chương] của Luật Hôn nhân và Gia đình quy định những gì?"
           
           - Nếu câu hỏi chỉ chứa "Mục [số mục]" mà không chứa "Chương [số chương]":
                    Kiểm tra lịch sử truy vấn, lấy thông tin chương gần nhất.
                    Nếu lịch sử không có thông tin, giả định mặc định là " Mục [số mục] của Luật Hôn nhân và Gia đình quy định những gì?".
                    Nếu lịch sử có thông tin, Chuyển đổi câu hỏi thành: "Chương [số chương], mục [số mục] của Luật Hôn nhân và Gia đình quy định những gì?"
         - *Trường hợp câu hỏi không chứa thông tin cụ thể*:
           - Xác định nội dung chính và làm rõ bối cảnh áp dụng (nếu cần).
           - Dựa vào lịch sử truy vấn history, lịch sử sẽ được làm ngữ cảnh thì chuyển đổi câu hỏi thành dạng đơn giản hóa để dễ dàng tra cứu nội dung luật.

    3. *Xử lý câu hỏi ngoài phạm vi luật*:
       - Nếu câu hỏi là dạng small talk và câu hỏi hiện tại là tiếng việt, ví dụ hỏi "Bạn là ai?", "Bạn làm được gì?", "Xin chào",... thì trả về:
         *Truy vấn chuyển đổi:* "Small talk".
       - Ngược lại, nếu không phải small talk và ngoài phạm vi pháp luật, trả về:
         *Truy vấn chuyển đổi:* "Đây không phải phạm vi lĩnh vực tôi biết. Tôi là chatbot hỗ trợ tư vấn Luật hôn nhân và gia đình. Bạn có câu hỏi gì về lĩnh vực này không?"


    """
            )
        ])

    def transform(self, query: str) -> str:
        chain = LLMChain(llm=self.llm, prompt=self.prompt_template, memory=self.memory)
        result = chain.run({"query": query})
        return result