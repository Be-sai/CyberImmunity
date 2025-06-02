import pytest
import requests
import time
from datetime import datetime, timedelta

# Конфигурация тестов
GATEWAY_URL = 'http://localhost:8001'
MOBILE_APP_URL = 'http://localhost:8000'
SMART_HOME_URL = 'http://localhost:8002'

# Тестовые данные
TEST_USER = {'username': 'admin', 'password': 'admin'}
TEST_COMMAND = {'command': 'turn_on_lights'}
TEST_SENSOR_DATA = {'type': 'temperature', 'value': 22.5}
TEST_NOTIFICATION = {'message': 'Test notification', 'priority': 'normal'}

@pytest.fixture(scope='module')
def setup():
    yield

def test_full_scenario():
    # 1. Тестирование авторизации через мобильное приложение
    login_response = requests.post(f'{MOBILE_APP_URL}/login', json=TEST_USER)
    assert login_response.status_code == 200
    assert login_response.json().get('success') is True
    
    # 2. Тестирование отправки команды
    command_response = requests.post(
        f'{MOBILE_APP_URL}/command',
        json=TEST_COMMAND
    )
    assert command_response.status_code == 200
    assert 'status' in command_response.json()
    
    # Проверяем, что команда записана в лог шлюза
    time.sleep(0.5)
    logs_response = requests.get(f'{GATEWAY_URL}/command_logs')
    assert TEST_COMMAND['command'] in [log['command'] for log in logs_response.json()]
    
    # 3. Тестирование отправки данных сенсора
    sensor_response = requests.post(
        f'{GATEWAY_URL}/sensor_data',
        json=TEST_SENSOR_DATA
    )
    assert sensor_response.status_code == 200
    
    # Проверяем, что данные сохранились
    time.sleep(0.5)
    sensor_check = requests.get(f'{GATEWAY_URL}/sensor_data')
    assert any(
        data['sensor_type'] == TEST_SENSOR_DATA['type'] and 
        data['value'] == TEST_SENSOR_DATA['value']
        for data in sensor_check.json()
    )
    
    # 4. Тестирование уведомлений
    # Отправляем уведомление
    notification_response = requests.post(
        f'{GATEWAY_URL}/notifications',
        json=TEST_NOTIFICATION
    )
    assert notification_response.status_code == 200
    
    # Проверяем получение уведомления через мобильное приложение
    time.sleep(0.5)
    notifications_response = requests.get(f'{MOBILE_APP_URL}/notifications')
    assert notifications_response.status_code == 200
    assert any(
        n['message'] == TEST_NOTIFICATION['message']
        for n in notifications_response.json()
    )
    
    # 5. Тестирование экстренного вызова
    emergency_response = requests.post(
        f'{SMART_HOME_URL}/emergency',
        json={'type': 'medical'}
    )
    assert emergency_response.status_code == 200
    assert 'contact' in emergency_response.json()
    
    # Проверяем, что уведомление о вызове создалось
    time.sleep(0.5)
    emergency_notifications = requests.get(f'{GATEWAY_URL}/notifications')
    assert any(
        'Emergency: medical called' in n['message'] and 
        n['priority'] == 'high'
        for n in emergency_notifications.json()
    )

def test_device_registration():
    # Тестирование регистрации устройства
    device_data = {
        'device_id': 'test_device_1',
        'type': 'light_switch'
    }
    response = requests.post(
        f'{SMART_HOME_URL}/devices/register',
        json=device_data
    )
    assert response.status_code == 200
    assert 'device_id' in response.json()
    
    # Проверяем, что устройство появилось в списке
    devices_response = requests.get(f'{SMART_HOME_URL}/devices')
    assert device_data['device_id'] in [d['name'] for d in devices_response.json()]

if __name__ == '__main__':
    pytest.main([__file__, '-v'])