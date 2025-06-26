import os
import random
import threading
import time
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from kafka_config import create_producer, TOPICS

HOST = '0.0.0.0'
PORT = 5010
MODULE_NAME = os.getenv('MODULE_NAME', 'SensorsController')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
producer = create_producer()

sensors = {
    "sockets": {"status": "on", "power": 230},
    "motion": {"status": "inactive", "last_triggered": None},
    "door": {"status": "closed", "locked": True},
    "fire": {"status": "normal", "smoke_level": 0.01},
    "gas": {"status": "normal", "concentration": 0.001},
    "water": {"status": "normal", "moisture": 0.0},
    "volume": {"status": "normal", "level_db": 35},
    "smart_lock": {"status": "locked", "battery": 95},
    "camera": {"status": "online", "last_event": "no_motion"}
}

def update_sensor_values():
    while True:
        for sensor in sensors:
            if sensor in ["fire", "gas", "water"]:
                if sensor == "fire":
                    sensors[sensor]["smoke_level"] = round(random.uniform(0.01, 0.05), 3)
                    if sensors[sensor]["smoke_level"] > 0.03:
                        sensors[sensor]["status"] = "alert"
                elif sensor == "gas":
                    sensors[sensor]["concentration"] = round(random.uniform(0.001, 0.005), 4)
                    if sensors[sensor]["concentration"] > 0.003:
                        sensors[sensor]["status"] = "alert"
                elif sensor == "water":
                    sensors[sensor]["moisture"] = round(random.uniform(0.0, 0.1), 2)
                    if sensors[sensor]["moisture"] > 0.05:
                        sensors[sensor]["status"] = "alert"
        
        producer.send(TOPICS['sensor_data'], sensors)
        time.sleep(5)

@app.route('/status', methods=['GET'])
def all_sensors():
    return jsonify(sensors), 200

@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({
        "status": e.code,
        "name": e.name,
        "message": e.description
    }), e.code

def start_web():
    threading.Thread(target=update_sensor_values, daemon=True).start()
    threading.Thread(target=lambda: app.run(
        host=HOST, port=PORT, debug=True, use_reloader=False
    )).start()