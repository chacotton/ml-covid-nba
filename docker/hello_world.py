import time
import requests
from sqlalchemy import create_engine
import pandas as pd
import sys

if __name__ == '__main__':
    system = sys.platform
    engine = create_engine(f'mysql+pymysql://admin:NBACovid19!@10.0.0.150/test_db')
    engine.connect()
    with open('./hello_world.txt', 'w') as f:
        f.write('Hello World\n')
        f.write(f'Time: {time.time()}')
