from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv

# Tải biến môi trường
load_dotenv()

class GPTHandler:
    def __init__(self, api_key: str = None, model: str = "gpt-4", temperature: float = 0.1, max_tokens: int = 2048):
        """
        Cấu hình GPT thông qua LangChain với các tham số mặc định.
        """
        # Cấu hình ChatOpenAI
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=api_key or os.getenv("OPENAI_API_KEY"),
        )

        # Prompt dành cho ChatOpenAI
        self.prompt_template = ChatPromptTemplate.from_messages([
            HumanMessagePromptTemplate.from_template("""
            Please answer the question: {question}.
            You are strictly required to use only the information provided below: {content}.
            Answer the question naturally
            Don't use phrases like "Dựa trên thông tin đã cung cấp" or similar.
            The included content may contain unrelated information, please only use relevant information to answer
            """)
        ])

    def process_query(self, content: str, question: str) -> str:
        # Sử dụng LLMChain để xử lý truy vấn
        chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
        return chain.run({"content": content, "question": question})
