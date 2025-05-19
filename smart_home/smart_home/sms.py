class SMSNotification:
    def send(self, message, recipient):
        print(f"SMS отправлено {recipient}: {message}")
        return True