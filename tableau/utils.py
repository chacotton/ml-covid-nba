from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
from pathlib import Path
from collections import namedtuple
import oracledb
import sys
from xgboost import XGBClassifier
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

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

def reformat_query(func):
    def method(command, **kwargs):
        if command.endswith('.sql'):
            with open(Path(__file__).resolve().parent / Path('queries') / Path(command)) as file:
                command = text(file.read())
                command.text = command.text.rstrip().rstrip(';')
        return func(command, **kwargs)
    return method


@reformat_query
def read_table(command: str, connection, index_col: str = None, **kwargs) -> pd.DataFrame:
    """
    Method to return dataset from database
    :param command: sql statement to execute
    :param connection: sql alchemy connection object
    :param index_col: name of primary key if desired as index
    :return: pandas DataFrame
    """
    df = pd.DataFrame(connection.execute(command, kwargs).fetchall())
    if index_col is not None:
        df.index = df.pop(index_col)
    return df


def resolve_path(path):
    path = Path(path)
    if path.exists():
        return path
    elif (path := Path('/mnt/ml-nba/models') / path).exists():
        return path
    else:
        raise FileNotFoundError


class WinProbWrapper:
    def __init__(self, file, session):
        self.model = XGBClassifier()
        self.model.load_model(resolve_path(file))
        self.session = session

    def predict(self, home_actives, away_actives, game_date, season, home):
        ha = {f'h{i + 1}': home_actives[i] if i < len(home_actives) else None for i in range(15)}
        aa = {f'a{i + 1}': away_actives[i] if i < len(away_actives) else None for i in range(15)}
        if all(v is None for v in ha.values()) and all(v is None for v in aa.values()):
            return [.5, .5]
        elif all(v is None for v in ha.values()):
            return [0, 1]
        elif all(v is None for v in aa.values()):
            return [1, 0]
        else:
            df = read_table('win_prob.sql', season=season, game_date=game_date,
                            team=home, **ha, **aa, connection=self.session)
            return self.model.predict_proba(df.iloc[:, 3:].values)[0][::-1]
