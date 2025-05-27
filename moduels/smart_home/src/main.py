from flask import Flask, request, jsonify, requests
from flask_sqlalchemy import SQLAlchemy
import threading
from datetime import datetime
from enum import Enum
from werkzeug.exceptions import HTTPException

HOST = '0.0.0.0'
PORT = 8002
GATEWAY_URL = 'http://gateway:8000'
DB_FILE = 'sqlite:///smart_home.db'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_FILE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class DeviceStatus(Enum):
    ONLINE = 'online'
    OFFLINE = 'offline'
    ERROR = 'error'

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Enum(DeviceStatus), default=DeviceStatus.ONLINE)
    last_active = db.Column(db.DateTime)

class EmergencyService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(50), nullable=False)
    contact = db.Column(db.String(100), nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()
    # Инициализация экстренных служб
    if not EmergencyService.query.first():
        services = [
            {'service_type': 'police', 'contact': '102'},
            {'service_type': 'fire', 'contact': '101'},
            {'service_type': 'medical', 'contact': '103'}
        ]
        for service in services:
            db.session.add(EmergencyService(**service))
        db.session.commit()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Это упрощённая имитация. На проде нужна авторизация и хэш.
    if username == 'admin' and password == 'admin':
        return jsonify({'token': 'mock-token'})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/notifications', methods=['GET'])
def get_notifications():
    response = request.get(f'{GATEWAY_URL}/notifications')
    return jsonify(response.json())

@app.route('/devices/register', methods=['POST'])
def register_device():
    data = request.json
    device_name = data.get('device_id')
    device_type = data.get('type')

    if not device_name or not device_type:
        return jsonify({'error': 'Missing fields'}), 400

    device = Device(name=device_name, device_type=device_type)
    db.session.add(device)
    db.session.commit()
    
    return jsonify({'status': 'registered', 'device_id': device.id})

@app.route('/command', methods=['POST'])
def execute_command():
    device_id = request.json.get('device_id')
    command = request.json.get('command')
    
    # Логика выполнения команд
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    # Отправка данных на шлюз
    request.post(f'{GATEWAY_URL}/command', 
                json={'command': f'{device.name}:{command}'})
    
    return jsonify({'status': 'executed'})

@app.route('/emergency', methods=['POST'])
def handle_emergency():
    emergency_type = request.json.get('type')
    service = EmergencyService.query.filter_by(service_type=emergency_type).first()
    
    if service:
        # Логика вызова службы
        requests.post(f'{GATEWAY_URL}/notifications',
                      json={'message': f'Emergency: {emergency_type} called',
                            'priority': 'high'})
        return jsonify({'contact': service.contact})
    
    return jsonify({'error': 'Service not available'}), 404

@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({
        "error": e.name,
        "status": e.code
    }), e.code

def start_server():
    threading.Thread(target=lambda: app.run(
        host=HOST, port=PORT, debug=True, use_reloader=False
    )).start()
