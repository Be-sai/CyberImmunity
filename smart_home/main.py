from user.user import User
from user.app import MobileApp
from smart_home.link import Link
from smart_home.router import Router
from user.web import WebServer
from smart_home.core import SmartHomeSystem
from smart_home.sms import SMSNotification
from smart_home.cloud import CloudNotification
from smart_home.emergency_call import EmergencyCall
from smart_home.security import SecuritySystem
from smart_home.sensors import SensorController
from smart_home.sockets import SmartSockets
from smart_home.volume import VolumeSensor
from smart_home.motion import MotionSensor
from smart_home.door import DoorSensor
from smart_home.finger_lock import FingerprintLock
from smart_home.fire import FireSensor
from smart_home.gas import GasSensor
from smart_home.water import WaterLeakSensor
from smart_home.power_supply import PowerSupply


def main():
    # Инициализация компонентов системы
    power = PowerSupply()
    user = User("test_user", "password123")
    app = MobileApp()
    link = Link()
    router = Router()
    web = WebServer()
    sms = SMSNotification()
    cloud = CloudNotification()
    emergency = EmergencyCall()
    smart_home = SmartHomeSystem()
    security = SecuritySystem()
    sensors = SensorController()
    sockets = SmartSockets()

    # Датчики
    volume_sensor = VolumeSensor(power)
    motion_sensor = MotionSensor(power)
    door_sensor = DoorSensor(power)
    finger_lock = FingerprintLock(power)
    fire_sensor = FireSensor(power)
    gas_sensor = GasSensor(power)
    water_sensor = WaterLeakSensor(power)

    # Подключение компонентов
    sensors.add_sensor(volume_sensor)
    sensors.add_sensor(motion_sensor)
    sensors.add_sensor(door_sensor)
    sensors.add_sensor(finger_lock)

    security.add_sensor(fire_sensor)
    security.add_sensor(gas_sensor)
    security.add_sensor(water_sensor)

    print("Система умного дома инициализирована и готова к работе")

    # Тестирование системы
    print("\nТестирование системы:")

    # 1. Вход пользователя
    print("\n1. Тест входа пользователя:")
    if app.login(user, "test_user", "password123"):
        print("Пользователь успешно вошел")

    # 2. Управление умным домом
    print("\n2. Тест управления умным домом:")
    app.send_command("включить свет")
    link.send_command("включить свет")
    router.route_command("включить свет", "Умные розетки")

    # 3. Работа с датчиками
    print("\n3. Тест работы датчиков:")
    motion_sensor.detect_motion(True)
    door_sensor.set_door_status(True)
    fire_sensor.detect_smoke(True)
    gas_sensor.detect_gas(False)
    water_sensor.detect_leak(False)

    print("Данные датчиков:", sensors.read_all())

    # 4. Мониторинг безопасности
    print("\n4. Тест системы безопасности:")
    security_alerts = security.check_security()
    print("Оповещения безопасности:", security_alerts)
    if security_alerts:
        print(security.trigger_alarm())
        cloud.send_emergency_alert(security_alerts)
        emergency.call("Мосгаз")

    # 5. Проверка замка
    print("\n5. Тест умного замка:")
    print("Проверка отпечатка:", finger_lock.verify_fingerprint("finger1"))


if __name__ == "__main__":
    main()