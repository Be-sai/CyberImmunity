import os
import threading
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
from kafka_config import create_producer, create_consumer, TOPICS

HOST = '0.0.0.0'
PORT = 5005
MODULE_NAME = os.getenv('MODULE_NAME', 'SmartHomeSystem')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
producer = create_producer()

EMERGENCY_SERVICES = {
    "fire": {"name": "Пожарная служба", "code": "01"},
    "police": {"name": "Полиция", "code": "02"},
    "gas": {"name": "Аварийная газовая", "code": "04"},
    "medical": {"name": "Скорая помощь", "code": "03"}
}

def start_command_consumer():
    consumer = create_consumer(TOPICS['commands'], group_id='smart_home')
    for message in consumer:
        command = message.value
        if command.get('command') == 'get_sensor_status':
            producer.send(TOPICS['sensor_data'], sensors)
        else:
            execute_command(command)

def execute_command(command):
    producer.send(TOPICS['system_logs'], {
        "module": MODULE_NAME,
        "event": "command_executed",
        "user": command.get('user'),
        "command": command.get('command')
    })
    
    producer.send(TOPICS['notifications'], {
        "message": f"Выполнена команда: {command.get('command')}",
        "recipient": command.get('user')
    })

def start_security_consumer():
    consumer = create_consumer(TOPICS['security_alerts'], group_id='smart_home')
    for message in consumer:
        alert = message.value
        handle_emergency(alert)

def handle_emergency(alert):
    service = EMERGENCY_SERVICES.get(alert.get('sensor'), EMERGENCY_SERVICES["fire"])
    producer.send(TOPICS['emergency_calls'], {
        "type": alert.get('sensor'),
        "reason": f"Обнаружена аномалия: {alert.get('sensor')}"
    })
    
    producer.send(TOPICS['notifications'], {
        "message": f"Вызвана {service['name']} ({service['code']})",
        "recipient": "admin"
    })

@app.errorhandler(HTTPException)
def handle_exception(e):
    producer.send(TOPICS['system_logs'], {
        "module": MODULE_NAME,
        "event": f"error_{e.code}",
        "message": e.description
    })
    return jsonify({
        "status": e.code,
        "name": e.name,
        "message": e.description
    }), e.code

def start_web():
    threading.Thread(target=lambda: app.run(
        host=HOST, port=PORT, debug=True, use_reloader=False
    )).start()
    threading.Thread(target=start_command_consumer, daemon=True).start()
    threading.Thread(target=start_security_consumer, daemon=True).start()