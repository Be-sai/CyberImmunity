class MotionSensor:
    def __init__(self, power_source):
        self.powered = power_source.supply_power(self)
        self.motion_detected = False

    def detect_motion(self, motion):
        self.motion_detected = motion

    def read(self):
        if not self.powered:
            return {"status": "inactive"}

        return {
            "status": "active",
            "motion": self.motion_detected,
            "alert": self.motion_detected,
            "message": "Обнаружено движение!" if self.motion_detected else "Нет движения"
        }