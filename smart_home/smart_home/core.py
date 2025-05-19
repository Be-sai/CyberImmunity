class SmartHomeSystem:
    def __init__(self):
        self.sensors = []
        self.devices = []

    def add_device(self, device):
        self.devices.append(device)

    def add_sensor(self, sensor):
        self.sensors.append(sensor)

    def process_command(self, command):
        print(f"Обработка команды умным домом: {command}")
        return True

    def get_sensor_data(self):
        return [sensor.read() for sensor in self.sensors]