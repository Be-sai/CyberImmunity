class GasSensor:
    def __init__(self, power_source):
        self.powered = power_source.supply_power(self)
        self.gas_leak = False

    def detect_gas(self, detected):
        self.gas_leak = detected

    def read(self):
        if not self.powered:
            return {"status": "inactive"}

        return {
            "status": "active",
            "gas_leak": self.gas_leak,
            "alert": self.gas_leak,
            "message": "Обнаружена утечка газа!" if self.gas_leak else "Норма"
        }