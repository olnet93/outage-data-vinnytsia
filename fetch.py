import requests
import json
from bs4 import BeautifulSoup

BASE_URL = "https://www.voe.com.ua/disconnection/detailed"

HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Mozilla/5.0"
}

QUEUES = [
    {"name": "Черга 1.1", "house_id": 26597, "street_id": 1652},
    {"name": "Черга 1.2", "house_id": 48650, "street_id": 1783},
    {"name": "Черга 2.1", "house_id": 32221, "street_id": 1329},
    {"name": "Черга 2.2", "house_id": 43696, "street_id": 1334},
    {"name": "Черга 3.1", "house_id": 43218, "street_id": 1391},
    {"name": "Черга 3.2", "house_id": 642115, "street_id": 1329},
    {"name": "Черга 4.1", "house_id": 624740, "street_id": 33276},
    {"name": "Черга 4.2", "house_id": 48483, "street_id": 1327},
    {"name": "Черга 5.1", "house_id": 47562, "street_id": 1286},
    {"name": "Черга 5.2", "house_id": 48439, "street_id": 1147},
    {"name": "Черга 6.1", "house_id": 41056, "street_id": 1113},
    {"name": "Черга 6.2", "house_id": 48348, "street_id": 1365},
]

def get_form_build_id():
    """Отримуємо актуальний form_build_id з головної сторінки пошуку"""
    r = requests.get(BASE_URL, headers=HEADERS)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    input_tag = soup.find("input", {"name": "form_build_id"})
    if input_tag:
        return input_tag["value"]
    raise ValueError("form_build_id не знайдено!")

def parse_table(html):
    """Парсимо таблицю годин відключень з insert HTML"""
    soup = BeautifulSoup(html, "html.parser")
    hours = []
    # Всі td у рядку
    for td in soup.select("td"):
        cls = td.get("class", [])
        # Вважаємо, що "disconnection" → True, інші → False
        hours.append({"disconnection": "disconnection" in cls})
    # Якщо менше 24 годин, добираємо False
    while len(hours) < 24:
        hours.append({"disconnection": False})
    return hours[:24]

def fetch_queue(queue):
    """Отримуємо дані для однієї черги"""
    form_build_id = get_form_build_id()
    data = {
        "city": "м.. Вінниця (Вінницька Область/М.Вінниця)",
        "city_id": "510100000",
        "street": "вулиця Келецька",
        "street_id": str(queue["street_id"]),
        "house": queue["name"].split()[-1],
        "house_id": str(queue["house_id"]),
        "search_type": "0",
        "search": "Показати",
        "form_build_id": form_build_id,
        "form_id": "disconnection_detailed_search_form"
    }
    r = requests.post(f"{BASE_URL}?ajax_form=1&_wrapper_format=drupal_ajax",
                      headers=HEADERS,
                      data=data)
    r.raise_for_status()
    res = r.json()
    # Знаходимо insert з таблицею
    html_insert = ""
    for cmd in res:
        if cmd.get("command") == "insert" and cmd.get("selector") == "#disconnection_detailed_search_form_wrapper":
            html_insert = cmd.get("data", "")
            break
    if not html_insert:
        raise ValueError(f"Таблиця не знайдена для {queue['name']}")
    hours = parse_table(html_insert)
    return {"name": queue["name"], "hours": hours}

def main():
    all_queues = []
    for q in QUEUES:
        try:
            data = fetch_queue(q)
            all_queues.append(data)
            print(f"{q['name']} ✅")
        except Exception as e:
            print(f"{q['name']} ❌ Помилка: {e}")
    # Зберігаємо JSON
    with open("data/vinnytsia.json", "w", encoding="utf-8") as f:
        json.dump({"queues": all_queues}, f, ensure_ascii=False, indent=2)
    print("vinnytsia.json збережено!")

if __name__ == "__main__":
    main()
