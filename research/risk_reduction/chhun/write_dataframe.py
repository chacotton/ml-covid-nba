import cx_Oracle
import config
import pandas as pd
from sqlalchemy import create_engine
from data import chance_of_victory

# https://www.oracle.com/news/connect/run-sql-data-queries-with-pandas.html


cx_Oracle.init_oracle_client(lib_dir="instantclient_19_8")
engine = create_engine('oracle+cx_oracle://{}:{}@{}'.format(config.username, config.password, config.dsn))


def PandastoSQL(data, tableName):
    """
    Method to covert Pandas Dataframe to SQL
    *Replace the table if table already exists
    """
    data.to_sql(tableName, engine, if_exists='append', index=False)

dataset = chance_of_victory.WinDataset(optimize=True).get_dataset()
tableName = 'pytabchhun'

PandastoSQL(dataset, tableName)






orders = """select * from pytabchhun"""
df_orders = pd.read_sql(orders, engine)

