#Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\venv\Scripts\Activate

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from fastapi.middleware.cors import CORSMiddleware
from langchain_elasticsearch import ElasticsearchRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from usecase2 import LegalDocumentSearch
import logging
import re
from LLM import GPTHandler
# from langchain.vectorstores import ElasticsearchRetriever
# from langchain.embeddings.huggingface import HuggingFaceEmbeddings

# Tạo một ứng dụng FastAPI
app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Elasticsearch parameters

# Tạo một đối tượng Elasticsearch

LLM = GPTHandler()

# Request model
class QueryRequest(BaseModel):
    query: str

# embedding = HuggingFaceEmbeddings(model_name="bkai-foundation-models/vietnamese-bi-encoder")
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
# Function to perform a vector search on Elasticsearch
def vector_query(search_query: str) -> Dict:
    vector = embedding.embed_query(search_query)  
    # print(vector)
    return {
        "knn": {
            "field": "embedding_vector",
            "query_vector": vector,
            "k": 5,
            "num_candidates": 10,
        }
    }

def dynamic_field_query(result: str) -> Dict:
    """
    Kiểm tra biến result để tìm từ khóa "điều" hoặc "chương" và tạo truy vấn tìm kiếm phù hợp.

    Args:
        result (str): Chuỗi cần kiểm tra (ví dụ: "Điều 8").

    Returns:
        Dict: Truy vấn Elasticsearch dựa trên trường phù hợp.
    """
    # Xác định trường dựa trên từ khóa
    result_lower = result.lower()  # Chuyển về chữ thường để so sánh
    # Use regex to match "điều" or "chương" followed by numbers as a full match
    matches = re.findall(r'\b(?:điều|chương)\s*\d+\b', result_lower)

    # Join the matches into a string or process them further
    filtered_result = ', '.join(matches)
    if "điều" in result_lower:
        field = "dieu"
        # search_query = result_lower.replace("điều", "").strip()  # Loại bỏ từ "điều" để lấy giá trị
    elif "chương" in result_lower:
        field = "chuong"
        # search_query = result_lower.replace("chương", "").strip()  # Loại bỏ từ "chương" để lấy giá trị
    else:
        raise ValueError("Result không chứa 'điều' hoặc 'chương'.")
    print("-----------------------------------")
    print(filtered_result)
    # Tạo truy vấn tìm kiếm
    return {
        "query": {
            "match_phrase": {
                field: filtered_result
            }
        },
        "size": 50 
    }


latest_history = {"question": "", "answer": ""}
# FastAPI route to get an answer from Elasticsearch
@app.post("/get_answer/")
async def get_answer(request: QueryRequest):
    global latest_history 
    search_query = request.query
    history = f"Câu hỏi trước đó: {latest_history['question']}\nĐáp án trước đó: {latest_history['answer']}"
    print("----------------", search_query,"-------------------")
    question , category = LLM.process_query(search_query, history)
    print(question,category,"------------------")
    if category == 0:
       search_engine = LegalDocumentSearch()
       question = question.lower()
       processed_question = search_engine.preprocess_question(question)
       content = search_engine.handle_question(processed_question)

       latest_history = {"question": search_query, "answer": content}
    # for result in results:
    #     content += result.page_content 

    # print("Content : ",content)
    # print ("Content: ", content)
    # result = LLM.process_query(content, search_query)
    # result,category = LLM.process_query(search_query)
    results = f"cate:{category} _content : {content} "
    # Trả về nội dung các kết quả tìm kiếm
    return {"results": results}
    # return {"results": content}
