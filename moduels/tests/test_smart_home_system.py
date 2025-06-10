import pytest
import requests

BASE_URL = "http://localhost:5005"
SENSORS_URL = "http://localhost:5010"

def test_user_authentication():
    """Тест авторизации пользователя"""
    response = requests.post(
        f"{BASE_URL}/access",
        json={"username": "admin", "password": "secret"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Доступ разрешен"

def test_sensor_data_retrieval():
    """Тест получения данных c датчиков"""
    response = requests.get(f"{BASE_URL}/sensors/status")
    assert response.status_code == 200
    data = response.json()
    assert "fire" in data
    assert "door" in data
    assert data["door"]["status"] in ["closed", "open"]

def test_command_execution():
    """Тест выполнения команды управления"""
    auth_response = requests.post(
        f"{BASE_URL}/access",
        json={"username": "admin", "password": "secret"}
    )
    
    response = requests.post(
        f"{BASE_URL}/execute",
        json={"command": "lock_doors", "user": "admin"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "Команда выполнена"
    
    # Проверяем состояние датчика двери
    sensor_data = requests.get(f"{SENSORS_URL}/door").json()
    assert sensor_data["door"]["locked"] is True

def test_emergency_handling():
    """Тест обработки экстренной ситуации"""
    response = requests.post(
        f"{BASE_URL}/emergency",
        json={"type": "fire", "reason": "Обнаружено задымление"}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "Тревога активирована"
    assert result["service"] == "Пожарная служба"
    assert "01" in result["code"]

def test_security_check():
    """Тест проверки системы безопасности"""
    response = requests.get(f"{BASE_URL}/security/check")
    assert response.status_code == 200
    
    data = response.json()
    assert "fire" in data
    assert "gas" in data
    assert data["fire"] in ["normal", "alert"]

def test_notification_system():
    """Тест системы уведомлений"""
    test_message = "Тестовое уведомление"
    response = requests.post(
        f"{BASE_URL}/execute",
        json={"command": "test_notify", "user": "admin"}
    )
    
    assert response.status_code == 200

@pytest.mark.parametrize("sensor_type", ["fire", "gas", "water"])
def test_critical_sensors(sensor_type):
    """Параметризованный тест критических датчиков"""
    response = requests.get(f"{SENSORS_URL}/{sensor_type}")
    assert response.status_code == 200
    data = response.json()
    assert sensor_type in data
    assert "status" in data[sensor_type]