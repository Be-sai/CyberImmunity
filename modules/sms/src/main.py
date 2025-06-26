import os
import threading
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
from kafka_config import create_producer, create_consumer, TOPICS

HOST = '0.0.0.0'
PORT = 5006
MODULE_NAME = os.getenv('MODULE_NAME', 'NotificationSystem')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
producer = create_producer()

def start_notification_consumer():
    consumer = create_consumer(TOPICS['notifications'], group_id='notifications')
    for message in consumer:
        notification = message.value
        print(f"[SMS] Sending to {notification['recipient']}: {notification['message']}")

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