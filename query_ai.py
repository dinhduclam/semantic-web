# Prompt gửi cho GPT
prompt = """
Hãy liệt kê tất cả các vị vua triều Nguyễn của Việt Nam.
Mỗi dòng gồm tên vua và một link DBpedia (nếu không có thì thay bằng link Wikipedia tiếng Anh).
Chỉ in ra dạng sau:
Tên vua – link
Không cần ghi gì thêm.
"""

import openai
from dotenv import load_dotenv
import os

load_dotenv()

# Lấy API key từ biến môi trường
openai.api_key = os.getenv("OPENAI_API_KEY")

response = openai.Completion.create(
    model="gpt-3.5-turbo",
    prompt= prompt,
    max_tokens=100
)

print(response.output_text)

# Lấy nội dung trả về
output_text = response.output_text

# Parse thành danh sách dict
king_list = []
for line in output_text.strip().split("\n"):
    if "–" in line:
        name, link = map(str.strip, line.split("–"))
        king_list.append({"name": name, "link": link})

# Ghi ra file JSON
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(king_list, f, ensure_ascii=False, indent=2)

print("Đã ghi danh sách dữ liệu vào xxx.json")
