import time
import requests
from sqlalchemy import create_engine
import pandas as pd
import sys

hosts = {
        "darwin": "127.0.0.1:3307",
        "linux": "10.0.0.150",
    }

if __name__ == '__main__':
    system = sys.platform
    engine = create_engine(f'mysql+pymysql://admin:NBACovid19!@{hosts[system]}/test_db')
    try:
        engine.connect()
        result = engine.execute('SELECT * FROM tags WHERE `key` = "xgboost" LIMIT 1;')
    except ConnectionError:
        result = None
    request = requests.get("https://www.basketball-reference.com/")
    with open('./hello_world.txt', 'w') as f:
        f.write('Hello World\n')
        f.write(f'Time: {time.time()}\n')
        f.write('Connecting to Basketball Reference ...\n')
        if request:
            f.write('Connection Succeeded!\n')
        else:
            f.write('Connection Failed\n')
        f.write('Connecting to Database ... \n')
        if result is not None:
            f.write('Connection Succeeded!\n')
            f.write('Attempting Query ...\n')
            f.write(str(next(result)))
        else:
            f.write('Connection Failed\n')



