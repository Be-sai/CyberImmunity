import os
import threading
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

HOST = '0.0.0.0'
PORT = 5008
MODULE_NAME = os.getenv('MODULE_NAME', 'EmergencyServices')
WEB_SERVER_URL = "http://web_server:5004"

app = Flask(__name__)

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
    
    print(f"[EMERGENCY] Calling {service_name}: {reason}")
    
    # Логирование вызова
    try:
        import requests
        requests.post(f"{WEB_SERVER_URL}/log", json={
            "module": MODULE_NAME,
            "event": "emergency_call",
            "service": service_name,
            "reason": reason
        })
    except:
        pass
    
    return jsonify({
        "status": "Вызов принят",
        "service": service_name,
        "reason": reason
    }), 200

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