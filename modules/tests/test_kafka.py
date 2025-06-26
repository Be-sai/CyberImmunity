import unittest
import requests
import time
from kafka import KafkaConsumer
import json

# Конфигурация тестов
APP = 'http://localhost:5001'
SMART_HOME = 'http://localhost:5005'
WEB_SERVER = 'http://localhost:5004'
SENSORS = 'http://localhost:5010'
SECURITY = 'http://localhost:5009'
EMERGENCY = 'http://localhost:5008'
SMS = 'http://localhost:5006'

# Настройка Kafka для тестов
KAFKA_BROKER = 'localhost:9092'
TEST_TOPIC = 'test_responses'
TEST_GROUP = 'test_consumer'

class SmartHomeKafkaTestSuite(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Создаем тестового консьюмера
        cls.consumer = KafkaConsumer(
            TEST_TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            auto_offset_reset='earliest',
            group_id=TEST_GROUP,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        time.sleep(2)  # Ждем инициализации

    def test_01_login_success(self):
        # Отправляем запрос на вход
        resp = requests.post(f"{APP}/login", json={"username": "admin", "password": "secret"})
        self.assertEqual(resp.status_code, 200)
        
        # Проверяем, что сообщение попало в Kafka
        message = next(self.consumer)
        self.assertEqual(message.value['type'], 'login_attempt')
        self.assertEqual(message.value['credentials']['username'], 'admin')

    def test_02_send_command(self):
        command = {"user": "admin", "command": "turn_on_lights"}
        resp = requests.post(f"{APP}/send_command", json=command)
        self.assertEqual(resp.status_code, 200)
        
        # Проверяем команду в Kafka
        message = next(self.consumer)
        self.assertEqual(message.value['command'], 'turn_on_lights')
        self.assertEqual(message.value['user'], 'admin')

    def test_03_sensor_status_all(self):
        resp = requests.get(f"{SENSORS}/status")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("fire", resp.json())

    def test_04_security_check(self):
        resp = requests.get(f"{SECURITY}/check")
        self.assertEqual(resp.status_code, 200)
        
        # Проверяем, что запрос на проверку датчиков отправлен
        message = next(self.consumer)
        self.assertEqual(message.value['command'], 'get_sensor_status')

    def test_05_emergency_call(self):
        payload = {"type": "fire", "reason": "Test emergency"}
        resp = requests.post(f"{EMERGENCY}/call", json=payload)
        self.assertEqual(resp.status_code, 200)
        
        # Проверяем экстренный вызов в Kafka
        message = next(self.consumer)
        self.assertEqual(message.value['service'], 'Пожарная служба')
        self.assertEqual(message.value['event'], 'emergency_call')

    def test_06_sms_notify(self):
        payload = {"message": "Test alert", "recipient": "test_user"}
        resp = requests.post(f"{SMS}/notify", json=payload)
        self.assertEqual(resp.status_code, 200)
        
        # Проверяем уведомление в Kafka
        message = next(self.consumer)
        self.assertIn("Test alert", message.value['message'])

    def test_07_history_log(self):
        resp = requests.get(f"{WEB_SERVER}/history")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("events", resp.json())

    def test_08_emergency_trigger_via_smart_home(self):
        payload = {"type": "gas", "reason": "Gas leak detected"}
        resp = requests.post(f"{SMART_HOME}/emergency", json=payload)
        self.assertEqual(resp.status_code, 200)
        
        # Проверяем два сообщения: логирование и вызов службы
        log_msg = next(self.consumer)
        self.assertEqual(log_msg.value['event'], 'emergency_triggered')
        
        call_msg = next(self.consumer)
        self.assertEqual(call_msg.value['service'], 'Аварийная газовая служба')

    def test_09_get_sensors_from_smart_home(self):
        resp = requests.get(f"{SMART_HOME}/sensors/status")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("gas", resp.text)

    def test_10_check_security_from_smart_home(self):
        resp = requests.get(f"{SMART_HOME}/security/check")
        self.assertEqual(resp.status_code, 200)

    @classmethod
    def tearDownClass(cls):
        cls.consumer.close()

if __name__ == '__main__':
    unittest.main()