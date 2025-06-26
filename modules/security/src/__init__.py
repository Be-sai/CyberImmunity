import os
from .main import start_web

MODULE_NAME = os.getenv('MODULE_NAME', 'SecuritySystem')

def main():
    print(f'[INFO] {MODULE_NAME} module starting...')
    start_web()