#Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\venv\Scripts\Activate

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware
from retriever import retrieval_embedding, retrieval_keyword
import re
from LLM import GPTHandler

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

    search_query = request.query

    question , category = LLM.process_query(search_query)
    print(question,category,"\n------------------")
    question = question.lower()

    # ví dụ: Nội dung điều 1 là gì
    if category == 0:
       processed_question = retrieve_keyword.preprocess_question(question)
       content = retrieve_keyword.search(processed_question)

    #ví dụ: Bao nhiêu tuổi được kết hôn
    if category == 2:
       content = retrieve_embedding.search(question)

    result = f"cate:{category} _content : {content} "
    # Trả về nội dung các kết quả tìm kiếm
    return {"results": result}
    # return {"results": content}