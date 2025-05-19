class Router:
    def __init__(self):
        self.connected = False

    def establish_connection(self):
        self.connected = True
        return self.connected

    def route_command(self, command, destination):
        if self.connected:
            print(f"Маршрутизация команды {command} к {destination}")
            return True
        return False