class WaterLeakSensor:
    def __init__(self, power_source):
        self.powered = power_source.supply_power(self)
        self.leak_detected = False

    def detect_leak(self, detected):
        self.leak_detected = detected

    def read(self):
        if not self.powered:
            return {"status": "inactive"}

        return {
            "status": "active",
            "leak_detected": self.leak_detected,
            "alert": self.leak_detected,
            "message": "Обнаружена протечка воды!" if self.leak_detected else "Норма"
        }