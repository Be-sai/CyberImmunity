import os
import requests
import threading
import time
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

HOST = '0.0.0.0'
PORT = 5005
MODULE_NAME = os.getenv('MODULE_NAME', 'SmartHomeSystem')

# Сервисные URL
WEB_SERVER_URL = 'http://server:5004'
SENSORS_URL = 'http://sensors:5010'
SECURITY_URL = 'http://security:5009'
SMS_URL = 'http://sms:5006'

EMERGENCY_SERVICES = {
    "fire": {"name": "Пожарная служба", "code": "01"},
    "police": {"name": "Полиция", "code": "02"},
    "gas": {"name": "Аварийная газовая", "code": "04"},
    "medical": {"name": "Скорая помощь", "code": "03"}
}

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

def log_event(event_data):
    try:
        requests.post(
            f'{WEB_SERVER_URL}/log',
            json=event_data,
            timeout=1
        )
    except requests.exceptions.RequestException:
        print(f"[ERROR] Logging failed for event: {event_data['event']}")

@app.route('/access', methods=['POST'])
def grant_access():
    credentials = request.json
    username = credentials.get('username', 'unknown')
    
    # Простая проверка учетных данных
    if username == 'admin' and credentials.get('password') == 'secret':
        log_event({
            "module": MODULE_NAME,
            "event": "access_granted",
            "user": username
        })
        return jsonify({"status": "Доступ разрешен"}), 200
    
    log_event({
        "module": MODULE_NAME,
        "event": "access_denied",
        "user": username
    })
    return jsonify({"status": "Доступ запрещен"}), 401

@app.route('/execute', methods=['POST'])
def execute_command():
    command = request.json
    user = command.get('user', 'unknown')
    cmd = command.get('command', 'unknown')
    
    log_event({
        "module": MODULE_NAME,
        "event": "command_executed",
        "user": user,
        "command": cmd
    })
    
    # Асинхронная отправка уведомления
    threading.Thread(target=send_notification, args=(
        f"Выполнена команда: {cmd}",
        user
    )).start()
    
    return jsonify({
        "status": "Команда выполнена",
        "command": cmd
    }), 200

@app.route('/emergency', methods=['POST'])
def handle_emergency():
    emergency_data = request.json
    service_type = emergency_data.get('type', 'fire')
    reason = emergency_data.get('reason', 'Неизвестная причина')
    
    log_event({
        "module": MODULE_NAME,
        "event": "emergency_triggered",
        "service": service_type,
        "reason": reason
    })

    service = EMERGENCY_SERVICES.get(service_type.lower(), EMERGENCY_SERVICES["fire"])
    
    send_notification(
        f"Вызвана {service['name']} ({service['code']}): {reason}",
        "admin"
    )
    
    return jsonify({
        "status": "Тревога активирована",
        "service": service['name'],
        "code": service['code'],
        "message": f"Причина: {reason}"
    }), 200

@app.route('/sensors/status', methods=['GET'])
def get_sensors_data():
    try:
        response = requests.get(f'{SENSORS_URL}/status', timeout=2)
        log_event({
            "module": MODULE_NAME,
            "event": "sensor_data_received"
        })
        return jsonify(response.json()), 200
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Sensors unavailable",
            "message": str(e)
        }), 503

@app.route('/security/check', methods=['GET'])
def security_check():
    try:
        response = requests.get(f'{SECURITY_URL}/check', timeout=2)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Security system unavailable",
            "message": str(e)
        }), 503

def send_notification(message, recipient):
    try:
        requests.post(
            f'{SMS_URL}/notify',
            json={"message": message, "recipient": recipient},
            timeout=1
        )
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Notification failed: {str(e)}")

@app.errorhandler(HTTPException)
def handle_exception(e):
    log_event({
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