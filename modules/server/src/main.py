import os
import threading
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
from kafka_config import create_producer, create_consumer, TOPICS

HOST = '0.0.0.0'
PORT = 5004
MODULE_NAME = os.getenv('MODULE_NAME', 'WebServer')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
producer = create_producer()
event_log = []

def start_log_consumer():
    consumer = create_consumer(TOPICS['system_logs'], group_id='webserver')
    for message in consumer:
        log_data = message.value
        event_log.append(log_data)
        print(f"[LOG] {log_data['module']}: {log_data['event']}")

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
    threading.Thread(target=start_log_consumer, daemon=True).start()