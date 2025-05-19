class FireSensor:
    def __init__(self, power_source):
        self.powered = power_source.supply_power(self)
        self.smoke_detected = False

    def detect_smoke(self, detected):
        self.smoke_detected = detected

    def read(self):
        if not self.powered:
            return {"status": "inactive"}

        return {
            "status": "active",
            "smoke_detected": self.smoke_detected,
            "alert": self.smoke_detected,
            "message": "Обнаружено задымление!" if self.smoke_detected else "Норма"
        }