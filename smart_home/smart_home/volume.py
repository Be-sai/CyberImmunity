class VolumeSensor:
    def __init__(self, power_source):
        self.powered = power_source.supply_power(self)

    def read(self):
        if self.powered:
            return {"status": "active", "volume": 42}
        return {"status": "inactive"}