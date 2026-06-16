import json
import os
from config import DATA_FILE, SOURCE_FILE

def load_rooms():
    #загрузка бд с фильтрацией
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                rooms = json.load(f)
                return[r for r in rooms if r.get('capacity') not in (0, 250)]
        except:
            pass
    return[]

def load_buildings():
    if os.path.exists(SOURCE_FILE):
        with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f).get('buildings', [])
    return[]

def get_unique_types(rooms):
    types = set()
    for r in rooms:
        t = r.get('parsed_type')
        if t and t != "Неизвестно":
            types.add(t)
    return sorted(list(types))

def get_capacities(rooms):
    caps = set()
    for r in rooms:
        c = r.get('capacity')
        if c:
            caps.add(c)
    return sorted(list(caps))

def filter_rooms(rooms, building_uid=None, min_capacity=0, room_type=None):
    res =[]
    for r in rooms:
        if r.get('isVirtualRoom'):
            continue
            
        cap = r.get('capacity') or 0
        if cap < min_capacity:
            continue

        if building_uid and r.get('buildingUid') != building_uid:
            continue
            
        if room_type:
            curr_type = r.get('parsed_type', '').lower()
            if room_type.lower() not in curr_type:
                continue
        
        res.append(r)
    return res
