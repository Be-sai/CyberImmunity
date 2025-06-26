import os
import threading
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
from kafka_config import create_producer, TOPICS

HOST = '0.0.0.0'
PORT = 5001
MODULE_NAME = os.getenv('MODULE_NAME', 'MobileApp')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
producer = create_producer()

@app.route('/login', methods=['POST'])
def login():
    credentials = request.json
    try:
        producer.send(TOPICS['access_logs'], {
            'type': 'login_attempt',
            'credentials': credentials,
            'source': MODULE_NAME
        })
        return jsonify({"status": "Login request sent"}), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to send login request: {str(e)}"
        }), 500

@app.route('/send_command', methods=['POST'])
def send_command():
    command = request.json
    try:
        producer.send(TOPICS['commands'], {
            'command': command.get('command'),
            'user': command.get('user'),
            'source': MODULE_NAME
        })
        return jsonify({"status": "Command sent"}), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to send command: {str(e)}"
        }), 500

def start_notification_consumer():
    consumer = create_consumer(TOPICS['notifications'], group_id='mobile_app')
    for message in consumer:
        notification = message.value
        print(f"[NOTIFICATION] {notification['message']}")

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
    threading.Thread(target=start_notification_consumer, daemon=True).start()