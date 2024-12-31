from elasticsearch import Elasticsearch
import re
from typing import List, Dict
from LLM_answer import LLM_finalanswer
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_elasticsearch import ElasticsearchRetriever

embedding = HuggingFaceEmbeddings(model_name="bkai-foundation-models/vietnamese-bi-encoder")

class retrieval_embedding:
    def __init__(self, host="localhost", port=9200, scheme="http", index="legal_document"):
        self.es = Elasticsearch([{ 'host': host, 'port': port, 'scheme': scheme }])
        self.index = index

    def vector_query(self, search_query: str) -> Dict:
        vector = embedding.embed_query(search_query)
        return {
            "query": {
                "function_score": {
                    "query": {
                        "match_all": {}  # Có thể thay bằng truy vấn khác nếu cần
                    },
                    "functions": [
                        {
                            "script_score": {
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, doc['embedding']) + 1.0",  # Cosine similarity calculation
                                    "params": {
                                        "query_vector": vector  # Vector tìm kiếm
                                    }
                                }
                            }
                        }
                    ],
                    "boost_mode": "multiply"  # Cách kết hợp điểm số của các truy vấn
                }
            },
            "_source": ["content", "dieu", "reference"]  # Các trường cần lấy
        }

    def extract_relevant_articles(self, results):
        relevant_articles = set()
        for result in results:
            dieu = result.metadata.get("_source", {}).get("dieu", None)
            reference = result.metadata.get("_source", {}).get("reference", [])

            if dieu:
                relevant_articles.add(dieu)

            if reference and isinstance(reference, list):
                relevant_articles.update(reference)
            elif reference:
                relevant_articles.add(reference)

        return list(relevant_articles)

    def build_query(self, relevant_articles: List[str]):
        return {
            "size": 100,
            "query": {
                "terms": {
                    "dieu.keyword": relevant_articles
                }
            }
        }

    def search(self, search_query: str):
        vector_retriever = ElasticsearchRetriever.from_es_params(
            index_name=self.index,
            body_func=self.vector_query,
            content_field="content",
            url="http://localhost:9200"
        )

        results = vector_retriever.invoke(search_query)
        relevant_articles = self.extract_relevant_articles(results)

        query = self.build_query(relevant_articles)
        response = self.es.search(index=self.index, body=query)

        contents = " ".join(
            hit["_source"].get("content", "")
            for hit in response["hits"]["hits"]
        )

        LLM_answer = LLM_finalanswer()

        return LLM_answer.answer(contents, search_query)




class retrieval_keyword:
    def __init__(self, host="localhost", port=9200, scheme="http", index="legal_document"):
        self.es = Elasticsearch([{ 'host': host, 'port': port, 'scheme': scheme }])
        self.index = index

    @staticmethod
    def roman_to_int_simple(roman):
        roman_map = {
            'i': 1, 'ii': 2, 'iii': 3, 'iv': 4,
            'v': 5, 'vi': 6, 'vii': 7, 'viii': 8,
            'ix': 9, 'x': 10
        }
        return roman_map.get(roman, None)

    def search_result(self, query):
        response = self.es.search(index=self.index, body=query)
        if response['hits']['total']['value'] > 0:
            return [hit['_source']['content'] for hit in response['hits']['hits']]
        return ["Không tìm thấy nội dung"]

    def search_article(self, article_number):
        query = {
            "query": {
                "match": {
                    "dieu": article_number
                }
            },
            "size": 10000
        }
        return self.search_result(query)

    def search_section_with_chapter(self, section_number, chapter_number):
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"muc": section_number}},
                        {"match": {"chuong": chapter_number}}
                    ]
                }
            },
            "size": 10000
        }
        return self.search_result(query)

    def search_chapter(self, chapter_number):
        query = {
            "query": {
                "match": {
                    "chuong": chapter_number
                }
            },
            "size": 10000
        }
        return self.search_result(query)

    @staticmethod
    def extract_numbers(question):
        article_matches = re.findall(r"điều (\d+)", question)
        section_matches = re.findall(r"mục (\d+)", question)
        chapter_matches = re.findall(r"chương (\d+)", question)
        return article_matches, section_matches, chapter_matches

    def preprocess_question(self, question):
        chapter_matches = re.findall(r"chương ([ivxlcdm]+)", question)
        for roman_chapter in chapter_matches:
            arabic_chapter = self.roman_to_int_simple(roman_chapter)
            if arabic_chapter is not None:
                question = question.replace(f"chương {roman_chapter}", f"chương {arabic_chapter}")
        return question
    
    def search(self, question: str) -> str:
        """
        Xử lý câu hỏi và trả về kết quả tìm kiếm dựa trên các từ khóa (Điều, Mục, Chương).
        """
        # Trích xuất các số từ câu hỏi
        article_numbers, section_numbers, chapter_numbers = self.extract_numbers(question)

        # Debug thông tin
        print(f"Điều: {article_numbers}")
        print(f"Mục: {section_numbers}")
        print(f"Chương: {chapter_numbers}")

        # Danh sách lưu kết quả tìm kiếm
        results = []

        # Nếu có số Điều trong câu hỏi
        if article_numbers:
            for article_number in article_numbers:
                results.extend(self.search_article(article_number))

        # Nếu có số Mục trong câu hỏi
        elif section_numbers:
            if not chapter_numbers:
                return "Bạn cần chỉ định đúng chương khi tìm mục."
            for section_number in section_numbers:
                for chapter_number in chapter_numbers:
                    results.extend(self.search_section_with_chapter(section_number, chapter_number))

        # Nếu có số Chương trong câu hỏi
        elif chapter_numbers:
            for chapter_number in chapter_numbers:
                results.extend(self.search_chapter(chapter_number))

        # Trả kết quả nếu không tìm thấy thông tin
        if not results:
            return "Không có thông tin liên quan trong câu hỏi."

        # Ghép kết quả thành chuỗi và trả về
        return "\n".join(results)
