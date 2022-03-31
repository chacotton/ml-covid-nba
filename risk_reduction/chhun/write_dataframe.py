import cx_Oracle
import config
import pandas as pd
from sqlalchemy import create_engine

# https://www.oracle.com/news/connect/run-sql-data-queries-with-pandas.html


cx_Oracle.init_oracle_client(lib_dir="instantclient_19_8")
engine = create_engine('oracle+cx_oracle://{}:{}@{}'.format(config.username, config.password, config.dsn))

players = ['Chhun', 'Ethan', 'Joe', 'Chase', 'Koushik', 'Suraj']
rank = [12, 23, 32, 43, 54, 61]
index = [10,11,12,13,14,15]

data = {
    'id' : rank,
    'data' : players
}

to_insert = pd.DataFrame(data)
print(to_insert)

to_insert.to_sql('pytabchhun', engine, if_exists='append', index=False)

orders = """select * from pytabchhun"""
df_orders = pd.read_sql(orders, engine)
print(df_orders)
