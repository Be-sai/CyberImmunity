import unittest
import requests

ROUTER = 'http://localhost:5003'
APP = 'http://localhost:5001'
SMART_HOME = 'http://localhost:5005'
WEB_SERVER = 'http://localhost:5004'
SENSORS = 'http://localhost:5010'
SECURITY = 'http://localhost:5009'
EMERGENCY = 'http://localhost:5008'
SMS = 'http://localhost:5006'

class SmartHomeTestSuite(unittest.TestCase):

    def test_01_login_success(self):
        resp = requests.post(f"{APP}/login", json={"username": "admin", "password": "secret"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Доступ разрешен", resp.text)

    def test_02_login_failure(self):
        resp = requests.post(f"{APP}/login", json={"username": "admin", "password": "wrong"})
        self.assertEqual(resp.status_code, 401)

    def test_03_send_command(self):
        command = {"user": "admin", "command": "turn_on_lights"}
        resp = requests.post(f"{APP}/send_command", json=command)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Команда выполнена", resp.text)

    def test_04_router_forward_login(self):
        payload = {"username": "admin", "password": "secret"}
        resp = requests.post(f"{ROUTER}/forward/login", json=payload)
        self.assertEqual(resp.status_code, 200)

    def test_05_router_invalid_service(self):
        resp = requests.post(f"{ROUTER}/forward/unknown_service", json={})
        self.assertEqual(resp.status_code, 404)

    def test_06_sensor_status_all(self):
        resp = requests.get(f"{SENSORS}/status")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("fire", resp.json())

    def test_07_sensor_individual(self):
        resp = requests.get(f"{SENSORS}/fire")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("fire", resp.json())

    def test_08_security_check(self):
        resp = requests.get(f"{SECURITY}/check")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), dict)

    def test_09_emergency_call(self):
        payload = {"type": "fire", "reason": "Test emergency"}
        resp = requests.post(f"{EMERGENCY}/call", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Вызов принят", resp.text)

    def test_10_sms_notify(self):
        payload = {"message": "Test alert", "recipient": "test_user"}
        resp = requests.post(f"{SMS}/notify", json=payload)
        self.assertEqual(resp.status_code, 200)

    def test_11_history_log(self):
        resp = requests.get(f"{WEB_SERVER}/history")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("events", resp.json())

    def test_12_emergency_trigger_via_smart_home(self):
        payload = {"type": "gas", "reason": "Gas leak detected"}
        resp = requests.post(f"{SMART_HOME}/emergency", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Тревога активирована", resp.text)

    def test_13_get_sensors_from_smart_home(self):
        resp = requests.get(f"{SMART_HOME}/sensors/status")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("gas", resp.text)

    def test_14_check_security_from_smart_home(self):
        resp = requests.get(f"{SMART_HOME}/security/check")
        self.assertEqual(resp.status_code, 200)

if __name__ == '__main__':
    unittest.main()