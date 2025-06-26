import os
import threading
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
from kafka_config import create_producer, create_consumer, TOPICS

HOST = '0.0.0.0'
PORT = 5003
MODULE_NAME = os.getenv('MODULE_NAME', 'Router')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
producer = create_producer()

ROUTING_TABLE = {
    "login": TOPICS['access_logs'],
    "command": TOPICS['commands'],
    "notification": TOPICS['notifications'],
    "log": TOPICS['system_logs'],
    "sensors": TOPICS['sensor_data'],
    "emergency": TOPICS['emergency_calls'],
    "security": TOPICS['security_alerts']
}

def start_command_router():
    consumer = create_consumer(TOPICS['commands'], group_id='router')
    for message in consumer:
        command = message.value
        producer.send(ROUTING_TABLE['command'], command)

def start_notification_router():
    consumer = create_consumer(TOPICS['notifications'], group_id='router')
    for message in consumer:
        notification = message.value
        producer.send(ROUTING_TABLE['notification'], notification)

@app.route('/forward/<service>', methods=['POST'])
def forward_request(service):
    if service not in ROUTING_TABLE:
        return jsonify({
            "error": "Service not available",
            "service": service
        }), 404
    
    try:
        producer.send(ROUTING_TABLE[service], request.json)
        return jsonify({"status": "message routed"}), 200
    except Exception as e:
        return jsonify({
            "error": "Routing failed",
            "service": service,
            "message": str(e)
        }), 500

@app.errorhandler(HTTPException)
def handle_exception(e):
    producer.send(TOPICS['system_logs'], {
        "module": MODULE_NAME,
        "event": "routing_error",
        "code": e.code,
        "message": e.description
    })
    return jsonify({
        "status": e.code,
        "name": e.name,
        "message": e.description
    }), e.code

def start_web():
    """Запуск HTTP-сервера и консьюмеров Kafka"""
    threading.Thread(target=lambda: app.run(
        host=HOST, port=PORT, debug=True, use_reloader=False
    )).start()
    
    threading.Thread(target=start_command_router, daemon=True).start()
    threading.Thread(target=start_notification_router, daemon=True).start()