import json
import os
import time
import random
import requests
from datetime import date
from config import SOURCE_FILE, DATA_FILE, API_SEARCH, API_TIMETABLE, HEADERS
import urllib3

#отключаем варнинги
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def safe_request(url, params):
    #обертка для обработки банов
    while True:
        time.sleep(random.uniform(3.0, 5.0))
        
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=10, verify=False)
            
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:
                print("\n\n!!! ПОЙМАНА КАПЧА (429) !!!")
                print("Зайди в браузер, реши капчу и нажми Enter здесь.")
                input("Жду Enter...")
                continue
            else:
                return None
        except Exception as e:
            print(f"Error: {e}, retrying...")
            time.sleep(5)

def get_site_id(name):
    data = safe_request(API_SEARCH, {'q': name})
    if not data: return None

    res = data.get('result',[]) or data.get('classrooms',[])
    
    #точное совпадение
    for item in res:
        if item.get('type') == 'classrooms' and item.get('name') == name:
            return item['id']
            
    #первое подходящее
    for item in res:
        if item.get('type') == 'classrooms':
            return item['id']
    return None

def get_room_details(room_id):
    today = date.today()
    iso_year, iso_week, _ = today.isocalendar()
    week_iso = f"{iso_year}-W{iso_week:02d}"

    data = safe_request(API_TIMETABLE, {'type': 'classrooms', 'id': room_id, 'weekISO': week_iso})
    
    if data and data.get('isSuccess'):
        try:
            details = data['result']['object']['details']
            for d in details:
                if d['name'] == 'Тип кабинета':
                    return d['values'][0]['value']
        except:
            pass
    return "Неизвестно"

def sync():
    if not os.path.exists(SOURCE_FILE):
        print(f"Нет файла {SOURCE_FILE}")
        return

    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        classrooms = data.get('classrooms',[])
        buildings = data.get('buildings', [])

    current_db =[]
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                current_db = json.load(f)
        except: pass
    
    done_names = {r['name'] for r in current_db}
    
    print(f"Всего: {len(classrooms)}. Уже готово: {len(done_names)}")
    print("Запускаю медленное сканирование (3-5 сек)...")
    
    new_db = list(current_db)
    count = 0

    for room in classrooms:
        name = room['name']
        cap = room.get('capacity', 0)
        
        if name in done_names: continue
        if room.get('isVirtualRoom'): continue
        
        #минус библиотека и актовый зал
        if cap in (0, 250): continue
            
        print(f"Scan: {name}...", end=" ", flush=True)
        
        site_id = get_site_id(name)
        
        if site_id:
            r_type = get_room_details(site_id)
            
            b_uid = room.get('buildingUid')
            b_name = next((b['name'] for b in buildings if b['uid'] == b_uid), "Неизвестно")
            
            entry = room.copy()
            entry['site_id'] = site_id
            entry['parsed_type'] = r_type
            entry['building_name'] = b_name
            
            new_db.append(entry)
            print(f"OK (ID: {site_id}, {r_type})")
        else:
            print("SKIP (Не найдено)")

        count += 1
        if count % 5 == 0:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(new_db, f, ensure_ascii=False, indent=4)
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_db, f, ensure_ascii=False, indent=4)
    print("Готово.")

if __name__ == "__main__":
    sync()
