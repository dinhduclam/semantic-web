import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

# Lấy API key từ biến môi trường
client = genai.Client(api_key=os.getenv("GEMINI_KEY"))


def read_from_file(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return None

    with open(path, "r", encoding="utf-8") as f:
        print(f"GeminiAI: Read from {path}")
        data = json.load(f)
        return data if data else None

# HistoricalDynasty <- liveIn <- HistoricalFigure
def get_historical_figure_list_from_dynasty(dynasty_name):
    output_file = f"{dynasty_name.replace(' ', '_').lower()}_kings.json"
    if (data := read_from_file(output_file)) is not None:
        return data

    prompt = f"""
    Hãy liệt kê tất cả các vị vua của {dynasty_name} ở Việt Nam.
    Mỗi dòng gồm tên vua và một link DBpedia của nhân vật sự kiện đó.
    Chỉ in ra dạng sau:
    Tên vua – link
    Không cần ghi gì thêm.
    Lưu ý: Không mã hóa link
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )

    # Lấy nội dung trả về
    output_text = response.text

    # Parse thành danh sách dict
    king_list = []
    for line in output_text.strip().split("\n"):
        if "–" in line:
            name, link = map(str.strip, line.split("–"))
            king_list.append({"name": name, "link": link})

    # Ghi ra file JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(king_list, f, ensure_ascii=False, indent=2)
    print(f"GeminiAI: Đã ghi danh sách các vị vua vào {output_file}")
    print(king_list)
    return king_list


# Site -> siteCommemorateEvent -> HistoricEvent
def get_historic_event_list_from_site(site_name):
    output_file = f"{site_name.replace(' ', '_').lower()}_events.json"
    if (data := read_from_file(output_file)) is not None:
        return data

    prompt = f"""
    Hãy liệt kê tất cả các sự kiện lịch sử gắn với {site_name} ở Việt Nam.
    Mỗi dòng gồm tên sự kiện và 1 link DBpedia gắn với sự kiện lịch sử đó.
    Chỉ in ra dạng sau:
    Tên sự kiện – link
    Không cần ghi gì thêm.
    Lưu ý: Không mã hóa link
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    # Lấy nội dung trả về
    output_text = response.text

    # Parse thành danh sách dict
    event_list = []
    for line in output_text.strip().split("\n"):
        if "–" in line:
            name, link = map(str.strip, line.split("–"))
            event_list.append({"name": name, "link": link})

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(event_list, f, ensure_ascii=False, indent=2)

    print(f"GeminiAI: Đã ghidanh sách các sự kiện lịch sử vào {output_file}")
    print(event_list)
    return event_list


# Site -> hasFestival -> Festival
def get_festival_list_from_site(site_name):
    output_file = f"{site_name.replace(' ', '_').lower()}_festivals.json"
    if (data := read_from_file(output_file)) is not None:
        return data

    prompt = f"""
    Hãy liệt kê tất cả các lễ hội (festival) gắn với {site_name} ở Việt Nam.
    Mỗi dòng gồm tên lễ hội và một link DBpedia gắn với lễ hội đó.
    Chỉ in ra dạng sau:
    Tên lễ hội – link
    Không cần ghi gì thêm.
    Lưu ý: Không mã hóa link
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )

    # Lấy nội dung trả về
    output_text = response.text

    # Parse thành danh sách dict
    festival_list = []
    for line in output_text.strip().split("\n"):
        if "–" in line:
            name, link = map(str.strip, line.split("–"))
            festival_list.append({"name": name, "link": link})

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(festival_list, f, ensure_ascii=False, indent=2)

    print(f"GeminiAI: Đã ghi danh sách các lễ hội vào {output_file}")
    print(festival_list)
    return festival_list

# kings = get_historical_figure_list_from_dynasty("Nguyễn dynasty")
# print(kings)

# events = get_historic_event_list_from_site("Hà Nội")
# print(events)

# festivals = get_festival_list_from_site("Hà Nội")
# print(festivals)
