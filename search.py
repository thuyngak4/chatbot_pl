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
from retriever import retrieval_embedding, retrieval_keyword
from LLM import GPTHandler
# from langchain.memory import ConversationBufferMemory

# # Tạo đối tượng ConversationBufferMemory
# memory = ConversationBufferMemory()
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

embedding = HuggingFaceEmbeddings(model_name="bkai-foundation-models/vietnamese-bi-encoder")
# embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

retrieve_keyword = retrieval_keyword()
retrieve_embedding= retrieval_embedding()
# FastAPI route to get an answer from Elasticsearch
@app.post("/get_answer/")
async def get_answer(request: QueryRequest):
    global latest_history 
    search_query = request.query

    print("----------------", search_query,"-------------------")
    question, category = LLM.process_query(search_query)
    print(question,category,"------------------")
    question = question.lower()
    if category == 0:
       processed_question = retrieve_keyword.preprocess_question(question)
       content = retrieve_keyword.search(processed_question)
       
    elif category == 2:
        content = LLM.answerer.answer_smalltalk(search_query,category)

    elif category == 4:
        retrived_content = retrieve_embedding.search(question)
        content = LLM.answerer.answrer_embed(retrived_content,search_query,category)
    if category == 1 or category == 3:
        content = question
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
