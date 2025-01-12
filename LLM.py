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

    def process_query(self, question: str) -> str:
        transformed_query = self.transformer.transform(question)
        processed_query, category = self.classifier.process_query(transformed_query)
        return processed_query,category