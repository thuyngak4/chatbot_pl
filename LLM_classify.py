import re
class Classify:
    @staticmethod
    def process_query(input_text: str):
        # Step 1: Remove "Truy vấn chuyển đổi:" prefix
        query = re.sub(r"^Truy vấn chuyển đổi:\s*", "", input_text).strip()
        query= re.search(r'"(.*?)"',query).group(1)
        # query = re.sub(r"^Truy vấn chuyển đổi:\s*", "", input_text).strip()

        print(query)
        # Step 2: Categorize
        if re.search(r"\b(điều|chương|mục)\s+\d+", query, re.IGNORECASE):
            category = 0 # Điều, Chương cụ thể
        elif re.search(r"\bTôi không hiểu bạn đang nói gì\b", query, re.IGNORECASE):
            category = 1 # Câu hỏi không hợp lệ
        elif re.search(r"\bSmall talk\b", query, re.IGNORECASE):
            category = 2 # Trả lời bằng small talk
        elif re.search(r"\bĐây không phải phạm vi lĩnh vực tôi biết. Tôi là chatbot hỗ trợ tư vấn Luật hôn nhân và gia đình. Bạn có câu hỏi gì về lĩnh vực này không?\b", query, re.IGNORECASE):
            category = 3 # Trả lời ngoài phạm vi lĩnh vực nó biết
        else:
            category = 4 # Trả lời bằng vector embed và metadata

        return query, category