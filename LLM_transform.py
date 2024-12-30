from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv

class Transform:
    def __init__(self, llm):
        self.llm = llm
        self.prompt_template = ChatPromptTemplate.from_messages([
            HumanMessagePromptTemplate.from_template(
                """
   Lịch sử truy vấn:
    {history}

    Câu hỏi hiện tại: {query}

    **Quy trình xử lý**:
    1. **Kiểm tra ngôn ngữ**:
       - Nếu câu hỏi không hoàn toàn bằng tiếng Việt, trả về:
         **Truy vấn chuyển đổi:** "Không có."

    2. **Dựa trên lịch sử truy vấn (nếu có)**:
       - Kiểm tra lịch sử truy vấn để xác định ngữ cảnh hoặc phạm vi mở rộng của câu hỏi hiện tại.
       - Nếu câu hỏi hiện tại không chỉ rõ phạm vi (ví dụ: chỉ đề cập "Mục" hoặc "Chương"), sử dụng thông tin từ truy vấn trước để bổ sung phạm vi đầy đủ. Ví dụ:
         - Nếu lịch sử hỏi về "Mục 1" và câu hiện tại hỏi "Chương 3," chuyển đổi câu hỏi thành:
           "Chương 3, Mục 1 của Luật Hôn nhân và Gia đình quy định những gì?"

    3. **Xác định phạm vi và chuyển đổi câu hỏi**:
       - Nếu câu hỏi liên quan đến Luật Hôn nhân và Gia đình Việt Nam:
         - **Trường hợp câu hỏi có số điều luật, chương, hoặc mục**:
           - Giữ nguyên số điều, chương, hoặc mục đã được đề cập.
           - Chuyển đổi câu hỏi thành dạng đầy đủ và rõ ràng. Ví dụ:
             "Điều [số điều luật]/ Chương [số chương] của Luật Hôn nhân và Gia đình quy định những gì?"
           - Nếu câu hỏi chỉ chứa "Mục [số mục]" mà không chứa "Chương [số chương]":
                    Kiểm tra lịch sử truy vấn, lấy thông tin chương gần nhất.
                    Nếu lịch sử không có thông tin, giả định mặc định là " Mục [số mục] của Luật Hôn nhân và Gia đình quy định những gì?".
                    Nếu lịch sử có thông tin, Chuyển đổi câu hỏi thành: "Chương [số chương], mục [số mục] của Luật Hôn nhân và Gia đình quy định những gì?"
         - **Trường hợp câu hỏi không chứa thông tin cụ thể**:
           - Xác định nội dung chính và làm rõ bối cảnh áp dụng (nếu cần).
           - Chuyển đổi câu hỏi thành dạng đơn giản hóa để dễ dàng tra cứu nội dung luật.

    4. **Xử lý câu hỏi ngoài phạm vi luật**:
       - Nếu câu hỏi không thuộc phạm vi Luật Hôn nhân và Gia đình, trả về:
         **Truy vấn chuyển đổi:** "Không có."

    Kết quả trả về chỉ bao gồm:
    **Truy vấn chuyển đổi:** "Dạng câu hỏi được đơn giản hóa"
    """
            )
        ])

    def transform(self, query: str,history: str) -> str:
        chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
        result = chain.run({"query": query,"history": history})
        return result
