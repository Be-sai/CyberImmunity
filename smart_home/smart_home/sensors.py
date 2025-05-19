class SensorController:
    def __init__(self):
        self.sensors = []

    def add_sensor(self, sensor):
        self.sensors.append(sensor)

    def read_all(self):
        return {sensor.__class__.__name__: sensor.read() for sensor in self.sensors}