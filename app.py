from flask import Flask, render_template, request, jsonify
from datetime import datetime
import api_client
import data_manager

app = Flask(__name__)
client = api_client.KLGTUClient()

#кэшируем при старте
ROOMS_DB = data_manager.load_rooms()
BUILDINGS = data_manager.load_buildings()
ROOM_TYPES = data_manager.get_unique_types(ROOMS_DB)
CAPACITIES = data_manager.get_capacities(ROOMS_DB)

@app.route('/')
def home():
    return render_template('index.html', 
                         buildings=BUILDINGS, 
                         types=ROOM_TYPES,
                         capacities=CAPACITIES)

@app.route('/api/candidates')
def get_candidates():
    b_uid = request.args.get('building')
    cap = int(request.args.get('capacity', 0))
    r_type = request.args.get('type')
    
    results = data_manager.filter_rooms(ROOMS_DB, b_uid, cap, r_type)
    results.sort(key=lambda x: x['name'])
    return jsonify(results)

@app.route('/api/check_status')
def check_status():
    room_id = request.args.get('id')
    date_str = request.args.get('date')
    #парсинг запрошенных пар
    pairs_arg = request.args.get('pairs', '')
    
    try:
        check_dt = datetime.strptime(date_str, "%Y-%m-%d")
        target_pairs = [int(p) for p in pairs_arg.split(',') if p.isdigit()]
    except:
        return jsonify({"error": "Bad params"}), 400

    schedule = client.get_schedule(room_id, check_dt.date())
    
    #карта занятости true=занято
    busy_map = {p: False for p in target_pairs}
    error_flag = False

    if schedule and schedule.get('isSuccess'):
        tt = schedule['result'].get('timetable', [])
        t_date = check_dt.strftime("%Y-%m-%d")

        for day in tt:
            #ищем нужный день
            if day['date'].startswith(t_date):
                items = day.get('items', [])
                for item in items:
                    if item['type'] == 'lesson':
                        #получаем номер пары из json
                        l_num = item['content']['timeSlot']['lessonNumber']
                        if l_num in busy_map:
                            busy_map[l_num] = True
                break
    else:
        error_flag = True

    #считаем сколько свободных из запрошенных
    free_count = sum(1 for p in target_pairs if not busy_map[p])
    is_fully_free = free_count == len(target_pairs)

    return jsonify({
        "busy_map": busy_map,
        "free_count": free_count,
        "is_fully_free": is_fully_free,
        "error": error_flag
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
