import os
import threading
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
from kafka_config import create_producer, create_consumer, TOPICS

HOST = '0.0.0.0'
PORT = 5009
MODULE_NAME = os.getenv('MODULE_NAME', 'SecuritySystem')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
producer = create_producer()

def start_sensor_consumer():
    consumer = create_consumer(TOPICS['sensor_data'], group_id='security')
    for message in consumer:
        sensor_data = message.value
        check_sensor_alerts(sensor_data)

def check_sensor_alerts(sensor_data):
    alerts = []
    for sensor, values in sensor_data.items():
        if values.get('status') != 'normal':
            alerts.append(sensor)
    
    if alerts:
        for alert_sensor in alerts:
            producer.send(TOPICS['security_alerts'], {
                "module": MODULE_NAME,
                "event": "security_alert",
                "sensor": alert_sensor,
                "status": sensor_data[alert_sensor]['status']
            })

@app.route('/check', methods=['GET'])
def security_check():
    producer.send(TOPICS['commands'], {
        "command": "get_sensor_status",
        "source": MODULE_NAME
    })
    return jsonify({"status": "Sensor check initiated"}), 200

def start_web():
    threading.Thread(target=lambda: app.run(
        host=HOST, port=PORT, debug=True, use_reloader=False
    )).start()
    threading.Thread(target=start_sensor_consumer, daemon=True).start()