import os
import requests
import threading
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

HOST = '0.0.0.0'
PORT = 5003
MODULE_NAME = os.getenv('MODULE_NAME', 'Router')

ROUTING_TABLE = {
    "login": "http://smart_home:5005/access",
    "command": "http://web_server:5004/process",
    "notification": "http://app:5001/notify",
    "log": "http://web_server:5004/log",
    "sensors": "http://sensors:5010/status"
}

app = Flask(__name__)

@app.route('/forward/<service>', methods=['POST'])
def forward_request(service):
    if service not in ROUTING_TABLE:
        return jsonify({
            "error": "Service not available",
            "service": service
        }), 404
    
    try:
        response = requests.post(
            ROUTING_TABLE[service],
            json=request.json,
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Service unavailable",
            "service": service,
            "message": str(e)
        }), 503

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