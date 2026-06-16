import os

BASE_URL = "https://rasp.klgtu.ru"
API_SEARCH = f"{BASE_URL}/api/v2/structure/search"
API_TIMETABLE = f"{BASE_URL}/api/v2/timetable/week"

#задержка запросов
REQUEST_DELAY = 0.2

DATA_FILE = "rooms_db.json"
SOURCE_FILE = "base_structure.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive"
}
