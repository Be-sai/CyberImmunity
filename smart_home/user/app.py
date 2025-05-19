class MobileApp:
    def __init__(self):
        self.connected = False

    def login(self, user, username, password):
        if user.authenticate(username, password):
            self.connected = True
            return True
        return False

    def send_command(self, command):
        if self.connected:
            print(f"Отправка команды: {command}")
            return True
        return False

    def receive_notification(self, message):
        print(f"Уведомление: {message}")