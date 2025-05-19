class Link:
    def __init__(self):
        self.connected = False

    def connect(self, router):
        self.connected = router.establish_connection()
        return self.connected

    def send_command(self, command):
        if self.connected:
            print(f"Команда передана по связи: {command}")
            return True
        return False