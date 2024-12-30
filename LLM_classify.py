import re
class Classify:
    @staticmethod
    def process_query(input_text: str):
        # Step 1: Remove "Truy vấn chuyển đổi:" prefix
        query = re.sub(r"^Truy vấn chuyển đổi:\s*", "", input_text).strip()
        query= re.search(r'"(.*?)"',query).group(1)
        # query = re.sub(r"^Truy vấn chuyển đổi:\s*", "", input_text).strip()

        # Step 2: Categorize
        if re.search(r"\b(điều|chương|mục)\s+\d+", query, re.IGNORECASE):
            category = 0 # Điều, Chương cụ thể
        elif re.search(r"\b(không có)\s+\d+", query, re.IGNORECASE):
            category = 1 # Câu hỏi không hợp lệ
        else:
            category = 2 # Trả lời bằng vector embed và metadata

        return query, category