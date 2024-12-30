from elasticsearch import Elasticsearch
import re
from LLM import GPTHandler

class LegalDocumentSearch:
    def __init__(self, host="localhost", port=9200, scheme="http", index="legal_document"):
        self.es = Elasticsearch([{
            'host': host,
            'port': port,
            'scheme': scheme
        }])
        self.index = index

    @staticmethod
    def roman_to_int_simple(roman):
        roman_map = {
            'i': 1, 'ii': 2, 'iii': 3, 'iv': 4,
            'v': 5, 'vi': 6, 'vii': 7, 'viii': 8,
            'ix': 9, 'x': 10
        }
        return roman_map.get(roman, None)

    def search_result(self, varl, query):
        response = self.es.search(index=self.index, body=query)
        if response['hits']['total']['value'] > 0:
            results = [hit['_source']['content'] for hit in response['hits']['hits']]
            return results
        else:
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
        return self.search_result(article_number, query)

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
        return self.search_result(f"Mục {section_number}, Chương {chapter_number}", query)

    def search_chapter(self, chapter_number):
        query = {
            "query": {
                "match": {
                    "chuong": chapter_number
                }
            },
            "size": 10000
        }
        return self.search_result(chapter_number, query)

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
            else:
                print(f"Chương '{roman_chapter}' không hợp lệ.")
        return question

    def handle_question(self, question):
        article_numbers, section_numbers, chapter_numbers = self.extract_numbers(question)

        print(f"Điều: {article_numbers}")
        print(f"Mục: {section_numbers}")
        print(f"Chương: {chapter_numbers}")

        results = []

        if article_numbers:
            for article_number in article_numbers:
                results.extend(self.search_article(article_number))

        elif section_numbers:
            if not chapter_numbers:
                return "Bạn cần chỉ định đúng chương khi tìm mục."
            for section_number in section_numbers:
                for chapter_number in chapter_numbers:
                    results.extend(self.search_section_with_chapter(section_number, chapter_number))

        elif chapter_numbers:
            for chapter_number in chapter_numbers:
                results.extend(self.search_chapter(chapter_number))

        if not results:
            return "Không có thông tin liên quan trong câu hỏi."

        return "\n".join(results)

