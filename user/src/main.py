from flask import Flask, request, jsonify
import requests
import threading
from werkzeug.exceptions import HTTPException

HOST = '0.0.0.0'
PORT = 5000
SERVER_URL = 'http://smart_home_server:8000'

app = Flask(__name__)

class MobileApp:
    def __init__(self):
        self.connected = False
        self.user_token = None
        self.notifications = []
        
    def login(self, username, password):
        response = requests.post(f'{SERVER_URL}/login', 
                               json={'username': username, 'password': password})
        if response.status_code == 200:
            self.connected = True
            self.user_token = response.json().get('token')
            return True
        return False
    
    def send_command(self, command):
        if not self.connected:
            return False
        
        response = requests.post(f'{SERVER_URL}/command',
                               json={'command': command},
                               headers={'Authorization': f'Bearer {self.user_token}'})
        return response.json()

@app.route('/command', methods=['POST'])
def handle_command():
    data = request.json
    command = data.get('command')
    if not command:
        return jsonify({'error': 'Command required'}), 400
    
    result = app.mobile_app.send_command(command)
    return jsonify(result)

@app.route('/notifications', methods=['GET'])
def get_notifications():
    return jsonify(app.mobile_app.notifications)

@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({
        "error": e.name,
        "status": e.code
    }), e.code

def start_app():
    app.mobile_app = MobileApp()
    threading.Thread(target=lambda: app.run(
        host=HOST, port=PORT, debug=True, use_reloader=False
    )).start()
