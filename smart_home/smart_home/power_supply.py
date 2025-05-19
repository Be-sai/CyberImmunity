class PowerSupply:
    def __init__(self):
        self.connected_devices = []

    def supply_power(self, device):
        self.connected_devices.append(device)
        return True