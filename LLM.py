from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv
from LLM_transform import Transform
from LLM_classify import Classify
# Tải biến môi trường
load_dotenv()

class GPTHandler:
    def __init__(self, api_key: str = None, model: str = "gpt-4o", temperature: float = 0.1, max_tokens: int = 2048):
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
        self.transformer = Transform(self.llm)
        self.classifier = Classify()
        # self.answer_handler = Answer(self.llm)

        # # Prompt dành cho ChatOpenAI
        # self.prompt_template = ChatPromptTemplate.from_messages([
        #     HumanMessagePromptTemplate.from_template("""
        #     Please answer the question: {question}.
        #     You are strictly required to use only the information provided below: {content}.
        #     Answer the question naturally and add additional information to that answer
        #     Don't use phrases like "Dựa trên thông tin đã cung cấp" or similar.
        #     The included content may contain unrelated information, please only use relevant information to answer
        #     """)
        # ])

    # def process_query(self, content: str, question: str) -> str:
    def process_query(self, question: str, history : str) -> str:
         # Step 1: Transform query
        transformed_query = self.transformer.transform(question , history)

        # Step 2: Classify transformed query
        processed_query, category = self.classifier.process_query(transformed_query)
        # # Sử dụng LLMChain để xử lý truy vấn
        # chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
        # return chain.run({"content": content, "question": question})
        return processed_query,category
