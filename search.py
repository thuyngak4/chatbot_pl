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
import logging
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

# Elasticsearch parameters
es_url = "http://localhost:9200"  
index_name = "legal_document"  

# Tạo một đối tượng Elasticsearch
es = Elasticsearch([es_url])
LLM = GPTHandler()

# Request model
class QueryRequest(BaseModel):
    query: str

embedding = HuggingFaceEmbeddings(model_name="bkai-foundation-models/vietnamese-bi-encoder")

# Function to perform a vector search on Elasticsearch
def vector_query(search_query: str) -> Dict:
    vector = embedding.embed_query(search_query)  
    return {
        "knn": {
            "field": "embedding",
            "query_vector": vector,
            "k": 5,
            "num_candidates": 10,
        }
    }

# FastAPI route to get an answer from Elasticsearch
@app.post("/get_answer/")
async def get_answer(request: QueryRequest):
    search_query = request.query
    vector_retriever = ElasticsearchRetriever.from_es_params(
        index_name=index_name,
        body_func=vector_query,
        content_field="content",
        url=es_url,
    )
    content = ""
    results = vector_retriever.invoke(search_query)
    for result in results:
        content += result.page_content 

    print(content)

    result = LLM.process_query(content, search_query)

    # Trả về nội dung các kết quả tìm kiếm
    return {"results": result}
