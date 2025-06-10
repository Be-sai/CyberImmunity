import pytest
import requests
import time
from threading import Thread
from smart_home.src.main import app as smart_home_app
from sensors.src.main import app as sensors_app

@pytest.fixture(scope='module')
def setup_system():
    smart_home_thread = Thread(target=lambda: smart_home_app.run(port=5005))
    sensors_thread = Thread(target=lambda: sensors_app.run(port=5010))
    
    smart_home_thread.daemon = True
    sensors_thread.daemon = True
    
    smart_home_thread.start()
    sensors_thread.start()
    
    time.sleep(2)
    
    yield