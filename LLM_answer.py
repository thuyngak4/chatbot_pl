from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv
class Answer:
    def __init__(self, llm):
        self.llm = llm
        """
        Configures GPT using LangChain with default parameters.
        """
        # Prompt templates for each category
        self.prompts = {
            2: ChatPromptTemplate.from_messages([
                HumanMessagePromptTemplate.from_template("""
                Câu hỏi hiện tại {question}
                Nếu người dùng đưa ra câu hỏi hoặc bình luận không liên quan trực tiếp đến luật hôn nhân và gia đình, thuộc dạng giao tiếp thân thiện (small talk), hãy trả lời với giọng điệu chuyên nghiệp nhưng nhẹ nhàng, tạo cảm giác gần gũi. Nếu thích hợp, hãy hướng người dùng quay lại các vấn đề liên quan đến luật hôn nhân và gia đình mà họ quan tâm.
                Ví dụ:

                Nếu người dùng nhận xét về thời tiết hoặc ngày hôm nay, hãy đáp lại thân thiện và hỏi xem họ có câu hỏi gì liên quan đến luật mà cần được giải đáp.
                Nếu người dùng chia sẻ tâm trạng, hãy đồng cảm và nhắc rằng chatbot luôn sẵn sàng hỗ trợ về các vấn đề luật pháp.
                Nếu người dùng hỏi về sở thích hoặc điều không liên quan, hãy trả lời chung chung một cách lịch sự và nhẹ nhàng quay lại nội dung chuyên môn
                Bạn tên là Achin.
                Bạn chỉ có thể giải đáp các câu hỏi liên quan đến Giải đáp thắc mắc về luật hôn nhân và gia đình, Tư vấn về quyền và nghĩa vụ, tìm kiếm chính xác nội dung điều luật.
                """)
            ]),
            4: ChatPromptTemplate.from_messages([
                HumanMessagePromptTemplate.from_template("""
                Câu hỏi hiện tại: {question}.
                Phân tích nội dung sau: {content}.
                Tạo câu trả lời chi tiết, dựa trên nội dung cung cấp. Không thêm những thông tin bên ngoài.
                Tránh sử dụng các cụm từ như "Dựa trên thông tin đã cung cấp" hoặc tương tự.
                Không dùng các từ có tác dụng thay thế như "nó".
                Trả lời đúng trọng tâm của câu hỏi và vài thông tin liên quan.
                """)
            ])
        }

    def answer_smalltalk(self, question: str, category: int) -> str:
        # Select the appropriate prompt template
        if category not in self.prompts:
            raise ValueError(f"Unsupported category: {category}")

        prompt_template = self.prompts[category]
        
        # Use LLMChain to process the query
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        return chain.run({"question": question})
    
    def answrer_embed(self, content: str, question: str, category: int) -> str:
        # Select the appropriate prompt template
        if category not in self.prompts:
            raise ValueError(f"Unsupported category: {category}")

        prompt_template = self.prompts[category]
        
        # Use LLMChain to process the query
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        return chain.run({"content": content, "question": question})