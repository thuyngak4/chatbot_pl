import os
from openai import OpenAI
from dotenv import load_dotenv
import time
import logging

# Tải các biến môi trường từ file .env
load_dotenv()

# Khởi tạo client OpenAI với khóa API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate(content, question):
    prompt = f"""
        Please answer the question {question}. You are strictly required to use only the information provided below {content}.
        Answer the question naturally and concisely.
        Don't use phrases like "based on information provided" or similar
    """
    
    try:
        # Gọi API với client chat completion
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="gpt-4o",
            temperature=0.1,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"API request failed: {e}")
        return "None"
