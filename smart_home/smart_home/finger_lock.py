class FingerprintLock:
    def __init__(self, power_source):
        self.powered = power_source.supply_power(self)
        self.registered_fingerprints = ["finger1", "finger2"]

    def verify_fingerprint(self, fingerprint):
        if not self.powered:
            return False

        return fingerprint in self.registered_fingerprints

    def read(self):
        if not self.powered:
            return {"status": "inactive"}

        return {
            "status": "active",
            "locked": True,
            "message": "Замок ожидает отпечаток пальца"
        }