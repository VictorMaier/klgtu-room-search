import time
import requests
import logging
from datetime import datetime
from config import HEADERS, API_TIMETABLE, REQUEST_DELAY
import urllib3

#отключаем шум ssl
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(message)s')
logger = logging.getLogger("API")

class KLGTUClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.session.verify = False

    def get_schedule(self, room_id, date_obj):
        #считаем неделю iso
        iso_year, iso_week, _ = date_obj.isocalendar()
        week_iso = f"{iso_year}-W{iso_week:02d}"
        
        params = {
            "type": "classrooms",
            "id": room_id,
            "weekISO": week_iso
        }

        try:
            time.sleep(REQUEST_DELAY)
            resp = self.session.get(API_TIMETABLE, params=params, timeout=5)
            
            if resp.status_code == 200:
                return resp.json()
            return None

        except requests.RequestException:
            return None