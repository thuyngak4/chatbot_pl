#Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\v_env\Scripts\Activate

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware
from retriever import retrieval_embedding, retrieval_keyword
import re
from LLM import GPTHandler
import time

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

LLM = GPTHandler()

# Request model
class QueryRequest(BaseModel):
    query: str

retrieve_keyword = retrieval_keyword()
retrieve_embedding= retrieval_embedding()

# FastAPI route to get an answer from Elasticsearch
@app.post("/get_answer/")
async def get_answer(request: QueryRequest):

    # Ghi lại thời gian bắt đầu
    start_time = time.time()

    search_query = request.query

    print("----------------", search_query,"-------------------")
    question, category = LLM.process_query(search_query)
    print(question,category,"------------------")
    
    if category == 0:
       question = question.lower()
       processed_question = retrieve_keyword.preprocess_question(question)
       content = retrieve_keyword.search(processed_question)
       
    elif category == 2:
        content = LLM.answerer.answer_smalltalk(search_query,category)
    elif category == 4:
        question = question.lower()
        retrived_content = retrieve_embedding.search(question)
        content = LLM.answerer.answrer_embed(retrived_content,search_query,category)
    if category == 1 or category == 3:
        content = question

    result = f"{content}"

    # Ghi lại thời gian kết thúc
    end_time = time.time()

    # Tính thời gian thực thi
    execution_time = end_time - start_time
    print(f"Time taken: {execution_time:.4f} seconds")

    # Trả về nội dung các kết quả tìm kiếm
    return {"results": result}
    # return {"results": content}