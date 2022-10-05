from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection
import pandas as pd
from pathlib import Path
from collections import namedtuple
from multiprocessing import Process, Queue
import oracledb
import sys
oracledb.version = "8.3.0"
sys.modules["cx_Oracle"] = oracledb
import cx_Oracle


DbArgs = namedtuple('DbArgs', 'user password dsn config wallet wallet_pass')
db_args = DbArgs(
    user="nba",
    password="SeniorDesign22",
    dsn="nba_low",
    config=Path(__file__).resolve().parent / Path("wallet"),
    wallet=Path(__file__).resolve().parent / Path("wallet"),
    wallet_pass="password1"
 )


def get_engine():
    return create_engine(
        f"oracle+cx_oracle://{db_args.user}:{db_args.password}@{db_args.dsn}",
        connect_args={
            "config_dir": db_args.config,
            "wallet_location": db_args.wallet,
            "wallet_password": db_args.wallet_pass
        }
    )


def reformat_query(func):
    def method(command, **kwargs):
        if command.endswith('.sql'):
            with open(Path(__file__).resolve().parent / Path('queries') / Path(command)) as file:
                command = text(file.read())
                command.text = command.text.rstrip().rstrip(';')
        return func(command, **kwargs)
    return method


@reformat_query
def read_table(command: str, connection: Connection = None, index_col: str = None, **kwargs) -> pd.DataFrame:
    """
    Method to return dataset from database
    :param command: sql statement to execute
    :param connection: sql alchemy connection object
    :param index_col: name of primary key if desired as index
    :return: pandas DataFrame
    """
    if connection is None:
        with get_engine().connect() as conn:
            df = pd.read_sql(command, conn, params=kwargs, index_col=index_col)
    else:
        df = pd.read_sql(command, connection, params=kwargs, index_col=index_col)
    return df


@reformat_query
def write_db(command: str, connection: Connection = None, **kwargs) -> bool:
    if connection is not None:
        connection.execute(command, **kwargs)
    else:
        with get_engine().begin() as conn:
            conn.execute(command, **kwargs)
    return True


def wrapper(ret, func, args, kwargs):
    ret.put(func(*args, **kwargs))


def timeout(timeout_, func, attempts=1, func_args=(), func_kwargs={}):
    queue = Queue(1)
    for _ in range(attempts):
        p1 = Process(target=wrapper, args=(queue, func, func_args, func_kwargs))
        p1.start()
        p1.join(timeout=timeout_)
        p1.kill()
        if p1.exitcode is None:
            continue
        elif p1.exitcode == 0:
            return queue.get()
    raise TimeoutError


