import os
import threading
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

HOST = '0.0.0.0'
PORT = 5006
MODULE_NAME = os.getenv('MODULE_NAME', 'NotificationSystem')
ROUTER_URL = "http://router:5003"

app = Flask(__name__)

@app.route('/notify', methods=['POST'])
def notify():
    data = request.json
    message = data.get('message', 'No message')
    recipient = data.get('recipient', 'all')
    
    print(f"[SMS] Sending to {recipient}: {message}")
    
    try:
        # Эмуляция отправки через роутер
        import requests
        requests.post(
            f"{ROUTER_URL}/forward/notification",
            json={
                "message": f"[NOTIFY] {message}",
                "recipient": recipient
            },
            timeout=1
        )
        return jsonify({"status": "sent"}), 200
    except Exception as e:
        return jsonify({
            "error": "Notification failed",
            "message": str(e)
        }), 500

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