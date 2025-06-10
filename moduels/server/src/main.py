import os
import threading
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

HOST = '0.0.0.0'
PORT = 5004
MODULE_NAME = os.getenv('MODULE_NAME', 'WebServer')

app = Flask(__name__)
event_log = []

@app.route('/log', methods=['POST'])
def log_event():
    data = request.json
    event_log.append(data)
    print(f"[LOG] {data['module']}: {data['event']}")
    return jsonify({"status": "logged"}), 200

@app.route('/process', methods=['POST'])
def process_command():
    command = request.json
    event_log.append({
        "type": "command",
        "command": command.get('command'),
        "user": command.get('user')
    })
    
    try:
        # Перенаправление в систему управления
        import requests
        response = requests.post(
            "http://smart_home:5005/execute",
            json=command,
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({
            "error": "Command processing failed",
            "message": str(e)
        }), 500

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify({
        "events": event_log,
        "count": len(event_log)
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