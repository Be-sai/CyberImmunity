import os

from .main import start_gateway


MODULE_NAME = os.getenv('MODULE_NAME')


def main():
    print(f'[DEBUG] {MODULE_NAME} started...')
    print(f'Running {MODULE_NAME}_api...')
    start_gateway()