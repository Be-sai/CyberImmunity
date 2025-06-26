import os
import random
import threading
import time
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

HOST = '0.0.0.0'
PORT = 5010
MODULE_NAME = os.getenv('MODULE_NAME', 'SensorsController')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Состояние датчиков
sensors = {
    "sockets": {"status": "on", "power": 230},
    "motion": {"status": "inactive", "last_triggered": None},
    "door": {"status": "closed", "locked": True},
    "fire": {"status": "normal", "smoke_level": 0.01},
    "gas": {"status": "normal", "concentration": 0.001},
    "water": {"status": "normal", "moisture": 0.0}
}

def update_sensor_values():
    """Периодическое обновление значений датчиков"""
    while True:
        for sensor in sensors:
            if sensor in ["fire", "gas", "water"]:
                # Случайные флуктуации значений
                if sensor == "fire":
                    sensors[sensor]["smoke_level"] = round(random.uniform(0.01, 0.05), 3)
                elif sensor == "gas":
                    sensors[sensor]["concentration"] = round(random.uniform(0.001, 0.005), 4)
                elif sensor == "water":
                    sensors[sensor]["moisture"] = round(random.uniform(0.0, 0.1), 2)
        
        time.sleep(5)

@app.route('/status', methods=['GET'])
def all_sensors():
    return jsonify(sensors), 200

@app.route('/<sensor_name>', methods=['GET'])
def get_sensor(sensor_name):
    if sensor_name in sensors:
        return jsonify({sensor_name: sensors[sensor_name]}), 200
    return jsonify({"error": "Sensor not found"}), 404

@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({
        "status": e.code,
        "name": e.name,
        "message": e.description
    }), e.code

def start_web():
    # Запуск фонового потока для обновления датчиков
    threading.Thread(target=update_sensor_values, daemon=True).start()
    threading.Thread(target=lambda: app.run(
        host=HOST, port=PORT, debug=True, use_reloader=False
    )).start()