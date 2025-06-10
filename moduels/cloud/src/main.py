import os
import threading
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

HOST = '0.0.0.0'
PORT = 5007
MODULE_NAME = os.getenv('MODULE_NAME', 'CloudServices')
EMERGENCY_URL = "http://emergency:5008"

app = Flask(__name__)

@app.route('/alert', methods=['POST'])
def alert():
    data = request.json
    reason = data.get('reason', 'Unknown emergency')
    
    print(f"[CLOUD] Emergency alert: {reason}")
    
    try:
        # Перенаправление в экстренные службы
        import requests
        response = requests.post(
            f"{EMERGENCY_URL}/call",
            json=data,
            timeout=3
        )
        return jsonify(response.json()), 200
    except Exception as e:
        return jsonify({
            "error": "Emergency service unavailable",
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