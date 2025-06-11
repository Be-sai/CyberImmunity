import os
import requests
import threading
import random
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

HOST = '0.0.0.0'
PORT = 5009
MODULE_NAME = os.getenv('MODULE_NAME', 'SecuritySystem')
SENSORS_URL = "http://sensors:5010"
SMART_HOME_URL = "http://smart_home:5005"
WEB_SERVER_URL = "http://server:5004"

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

def log_event(event_data):
    try:
        requests.post(f"{WEB_SERVER_URL}/log", json=event_data, timeout=1)
    except:
        print(f"[SECURITY] Logging failed: {event_data}")

@app.route('/check', methods=['GET'])
def security_check():
    sensors_to_check = ["fire", "gas", "water"]
    status = {}
    alerts = []
    
    for sensor in sensors_to_check:
        try:
            response = requests.get(f"{SENSORS_URL}/{sensor}", timeout=1)
            sensor_data = response.json()
            inner_data = sensor_data.get(sensor, {})
            sensor_status = inner_data.get('status', 'unknown')
            
            status[sensor] = sensor_status

            if sensor_status != 'normal':
                alerts.append(sensor)

        except requests.exceptions.RequestException:
            status[sensor] = "error"
    
    if alerts:
        for alert_sensor in alerts:
            try:
                requests.post(
                    f"{SMART_HOME_URL}/emergency",
                    json={
                        "type": alert_sensor,
                        "reason": f"Обнаружена аномалия: {alert_sensor}"
                    },
                    timeout=2
                )
                log_event({
                    "module": MODULE_NAME,
                    "event": "security_alert",
                    "sensor": alert_sensor
                })
            except:
                pass
    
    return jsonify(status), 200

@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({
        "status": e.code,
        "name": e.name,
        "message": e.description
    }), e.code

def start_web():
    threading.Thread(target=lambda: app.run(
        host=HOST, port=PORT, debug=True, use_reloader=False
    )).start()