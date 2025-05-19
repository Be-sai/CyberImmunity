class SecuritySystem:
    def __init__(self):
        self.sensors = []
        self.alarm_status = False

    def add_sensor(self, sensor):
        self.sensors.append(sensor)

    def check_security(self):
        alerts = []
        for sensor in self.sensors:
            reading = sensor.read()
            if reading.get('alert', False):
                alerts.append({
                    'sensor': sensor.__class__.__name__,
                    'message': reading['message']
                })
        return alerts

    def trigger_alarm(self):
        self.alarm_status = True
        return "Тревога! Обнаружена угроза безопасности"