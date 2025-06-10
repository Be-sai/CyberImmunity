import os
import requests
import threading
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

HOST = '0.0.0.0'
PORT = 5001
MODULE_NAME = os.getenv('MODULE_NAME', 'MobileApp')
ROUTER_URL = "http://router:5003"

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    credentials = request.json
    try:
        response = requests.post(
            f"{ROUTER_URL}/forward/login",
            json=credentials,
            timeout=3
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "error",
            "message": f"Connection error: {str(e)}"
        }), 503

@app.route('/send_command', methods=['POST'])
def send_command():
    command = request.json
    try:
        response = requests.post(
            f"{ROUTER_URL}/forward/command",
            json=command,
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "error",
            "message": f"Command delivery failed: {str(e)}"
        }), 503

@app.route('/notify', methods=['POST'])
def receive_notification():
    notification = request.json
    print(f"[NOTIFICATION] {notification['message']}")
    return jsonify({"status": "received"}), 200

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