class DoorSensor:
    def __init__(self, power_source):
        self.powered = power_source.supply_power(self)
        self.is_open = False

    def set_door_status(self, is_open):
        self.is_open = is_open

    def read(self):
        if not self.powered:
            return {"status": "inactive"}

        return {
            "status": "active",
            "door_open": self.is_open,
            "alert": self.is_open,
            "message": "Дверь открыта!" if self.is_open else "Дверь закрыта"
        }