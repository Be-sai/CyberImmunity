from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import threading
from datetime import datetime
from werkzeug.exceptions import HTTPException

HOST = '0.0.0.0'
PORT = 8001
DB_FILE = 'sqlite:///gateway.db'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_FILE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class CommandLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    command = db.Column(db.String(200), nullable=False)
    response = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(20), default='normal')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/notifications', methods=['GET'])
def list_notifications():
    notifications = Notification.query.order_by(Notification.timestamp.desc()).all()
    return jsonify([
        {
            'message': n.message,
            'priority': n.priority,
            'timestamp': n.timestamp.isoformat()
        } for n in notifications
    ])

@app.route('/command', methods=['POST'])
def handle_command():
    command = request.json.get('command')
    if not command:
        return jsonify({'error': 'Command required'}), 400
    
    # Здесь логика обработки команд
    log = CommandLog(command=command, response='OK')
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/sensor_data', methods=['POST'])
def receive_sensor_data():
    data = request.json
    sensor = SensorData(
        sensor_type=data.get('type'),
        value=data.get('value')
    )
    db.session.add(sensor)
    db.session.commit()
    return jsonify({'status': 'received'})

@app.route('/notifications', methods=['POST'])
def receive_notification():
    notification = Notification(
        message=request.json.get('message'),
        priority=request.json.get('priority', 'normal')
    )
    db.session.add(notification)
    db.session.commit()
    return jsonify({'status': 'received'})

@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({
        "error": e.name,
        "status": e.code
    }), e.code

@app.route('/command_logs', methods=['GET'])
def get_command_logs():
    logs = CommandLog.query.order_by(CommandLog.timestamp.desc()).all()
    return jsonify([
        {
            'command': log.command,
            'response': log.response,
            'timestamp': log.timestamp.isoformat()
        } for log in logs
    ])

@app.route('/sensor_data', methods=['GET'])
def get_sensor_data():
    data = SensorData.query.order_by(SensorData.timestamp.desc()).all()
    return jsonify([
        {
            'sensor_type': d.sensor_type,
            'value': d.value,
            'timestamp': d.timestamp.isoformat()
        } for d in data
    ])

def start_gateway():
    threading.Thread(target=lambda: app.run(
        host=HOST, port=PORT, debug=True, use_reloader=False
    )).start()