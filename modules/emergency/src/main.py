import os
import threading
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
from kafka_config import create_producer, create_consumer, TOPICS

HOST = '0.0.0.0'
PORT = 5008
MODULE_NAME = os.getenv('MODULE_NAME', 'EmergencyServices')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
producer = create_producer()

SERVICES = {
    "fire": "Пожарная служба",
    "police": "Полиция",
    "gas": "Аварийная газовая служба",
    "medical": "Скорая помощь",
    "water": "Аварийная водная служба"
}

@app.route('/call', methods=['POST'])
def call_service():
    data = request.json
    service_type = data.get('type', 'fire')
    reason = data.get('reason', 'Неизвестная причина')
    
    service_name = SERVICES.get(service_type, "Общая экстренная служба")
    
    producer.send(TOPICS['emergency_calls'], {
        "module": MODULE_NAME,
        "event": "emergency_call",
        "service": service_name,
        "reason": reason
    })
    
    return jsonify({
        "status": "Вызов принят",
        "service": service_name,
        "reason": reason
    }), 200

def start_emergency_consumer():
    consumer = create_consumer(TOPICS['emergency_calls'], group_id='emergency')
    for message in consumer:
        call = message.value
        print(f"[EMERGENCY] Calling {call['service']}: {call['reason']}")

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
    threading.Thread(target=start_emergency_consumer, daemon=True).start()