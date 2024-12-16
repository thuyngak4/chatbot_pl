from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from LLM import generate
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả các domain, bạn có thể thay thế "*" bằng domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả các phương thức
    allow_headers=["*"],  # Cho phép tất cả các header
)

# Kết nối với Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Khởi tạo mô hình SentenceTransformer
embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

class QueryRequest(BaseModel):
    query: str

def search_in_elasticsearch(query, embedding_model, es_client):
    # Tạo vector nhúng cho câu hỏi
    query_vector = embedding_model.encode(query).tolist()

    # Truy vấn Elasticsearch
    response = es_client.search(
        index="law_chunks",
        body={
            "size": 5,  # Số lượng kết quả cần trả về
            "query": {
                "script_score": {
                    "query": { "match_all": {} },
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding_vector') + 1.0",
                        "params": { "query_vector": query_vector }
                    }
                }
            }
        }
    )
    return response['hits']['hits']

@app.post("/get_answer/")
async def get_answer(request: QueryRequest):
    # Lấy câu hỏi từ yêu cầu
    query = request.query

    # Tìm kiếm trong Elasticsearch
    results = search_in_elasticsearch(query, embedding_model, es)
    
    # Tạo nội dung trả lời từ kết quả Elasticsearch
    content = "Luật Hôn nhân và Gia đình \n"
    for result in results:
        content += result["_source"]["metadata"]["clause_text"]
    
    # Sinh câu trả lời từ LLM (ChatGPT hoặc mô hình tương tự)
    reply = generate(content, query)

    # Trả về câu trả lời cho người dùng
    return {"answer": reply}
