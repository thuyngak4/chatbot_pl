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
        },
        "_source": ["content", "dieu", "reference"]
    }

def build_query(relevant_articles: List[str]):
    """
    Xây dựng truy vấn Elasticsearch để tìm tài liệu có `dieu` nằm trong relevant_articles.
    """
    return {
        "size": 100,
        "query": {
            "terms": {
                "dieu.keyword": relevant_articles  # Sử dụng .keyword để tìm khớp chính xác
            }
        }
    }

def extract_relevant_articles(results):
    relevant_articles = set()  # Sử dụng set để loại bỏ trùng lặp
    for result in results:
        dieu = result.metadata.get("_source", {}).get("dieu", None)
        reference = result.metadata.get("_source", {}).get("reference", [])

        # Thêm dieu vào danh sách nếu có
        if dieu:
            relevant_articles.add(dieu)

        # Thêm các giá trị trong reference nếu có
        if reference and isinstance(reference, list):
            relevant_articles.update(reference)
        elif reference:  # Nếu reference không phải là list
            relevant_articles.add(reference)
    
    return list(relevant_articles)

    
 # FastAPI route to get an answer from Elasticsearch
@app.post("/get_answer/")
async def get_answer(request: QueryRequest):
    search_query = request.query
    vector_retriever = ElasticsearchRetriever.from_es_params(
        index_name=index_name,
        body_func=vector_query,
        content_field="content",
        url=es_url
    )

    results = vector_retriever.invoke(search_query)
    relevant_articles = extract_relevant_articles(results)

    query = build_query(relevant_articles)
    response = es.search(index=index_name, body=query)

    # Trích xuất content từ kết quả
    contents = " ".join(
    hit["_source"]["content"]
    for hit in response["hits"]["hits"]
    if "content" in hit["_source"]
)
    print(contents)
    print(relevant_articles)

    result = LLM.process_query(contents, search_query)

    # Trả về nội dung các kết quả tìm kiếm
    return {"results": result}