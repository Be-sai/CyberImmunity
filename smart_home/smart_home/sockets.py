class SmartSockets:
    def __init__(self):
        self.sockets = {}

    def add_socket(self, socket_id):
        self.sockets[socket_id] = {"status": "off", "power": 0}

    def toggle_socket(self, socket_id, status):
        if socket_id in self.sockets:
            self.sockets[socket_id]["status"] = "on" if status else "off"
            return True
        return False

    def get_status(self, socket_id):
        return self.sockets.get(socket_id, {"error": "socket not found"})