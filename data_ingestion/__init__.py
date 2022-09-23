from data_ingestion.main import join_player_stats, update_player_stats, update_team_stats, update_roster
from collections import namedtuple
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from pathlib import Path
import oracledb
from data_ingestion.constants import *
from sqlalchemy import create_engine
import sys
oracledb.version = "8.3.0"
sys.modules["cx_Oracle"] = oracledb
import cx_Oracle



class Dataset(ABC):
    """Abstract base class for generating datasets"""

    DataFile = namedtuple("DataFile", "folder file")

    files = {
        ADJUSTED_SHOOTING_21: DataFile('player_data/', 'nba_adjusted_shooting_2021_2022.csv'),
        ADVANCED_21: DataFile('player_data/', 'nba_advanced_2021_2022.csv'),
        PER_GAME: DataFile('player_data/', 'nba_per_game_2021_2022.csv'),
        PLAY_BY_PLAY_21: DataFile('player_data/', 'nba_play_by_play_2021_2022.csv'),
        SHOOTING_21: DataFile('player_data/', 'nba_shooting_2021_2022.csv'),
        TEAM: DataFile('team_data/', 'nba_team_21-22.csv')
    }

    db_args = {
        "user": "nba",
        "password": "SeniorDesign22",
        "dsn": "nba_low",
        "config_dir": Path(__file__).resolve().parent / Path("wallet"),
        "wallet_location": Path(__file__).resolve().parent / Path("wallet"),
        "wallet_password": "password1",
    }

    def __init__(self, name: str):
        """
        Initialization method
        :param name: str, name of dataset
        """
        self._dataframe = None
        self._stat_table_names = []
        self.__name__ = name

    def __str__(self):
        """
        :return: name of dataset
        """
        return self.__name__

    def __repr__(self):
        """
        :return: name of dataset
        """
        return f'{self.__name__} Dataset Object'

    @staticmethod
    def _split_player_name(name: str):
        """
        Helper method to split components of player name
        :param name: str
        :return: player_id, first_name, last_name
        """
        name = name.split(' ', 1)
        first = name[0]
        last, player = name[-1].split('\\', 1)
        return player, first, last

    @staticmethod
    def _get_engine():
        return create_engine(
            f"oracle+cx_oracle://{Dataset.db_args['user']}:{Dataset.db_args['password']}@{Dataset.db_args['dsn']}",
            connect_args={
                "config_dir": Dataset.db_args['config_dir'],
                "wallet_location": Dataset.db_args['wallet_location'],
                "wallet_password": Dataset.db_args['wallet_password']
            }
        )

    @classmethod
    def _read_csv(cls, name: DataFile) -> pd.DataFrame:
        """
        Helper method to read csv files
        :param name: DataFile call by self.files[CONSTANT_NAME]
        :return: pandas DataFrame
        """
        return pd.read_csv(Path(__file__).parent.parent/ 'data' / name.folder / name.file)

    @classmethod
    def _read_db(cls, command: str, **kwargs) -> pd.DataFrame:
        """
        Method to return dataset from database
        :param command: sql statement to execute
        :return: pandas DataFrame
        """
        with cls._get_engine().connect() as conn:
            df = pd.read_sql(command, conn, params=kwargs)
        return df

    @classmethod
    def _player_data(cls, name: DataFile) -> pd.DataFrame:
        """
        Returns DataFrame indexed by player identifier and aggregated by a weighted mean relative to minutes played
        :param name: DataFile containing csv to load
        :return: pandas DataFrame
        """
        df = cls._read_csv(name)
        df = df.dropna(axis=1, how='all').dropna(axis=0, how='all').fillna(0)
        df[['Player', 'First Name', 'Last Name']] = df.apply(lambda row: cls._split_player_name(row.Player),
                                                             result_type='expand', axis=1)
        df.index = df.pop('Player')
        df = df.iloc[:, df.columns.get_loc('MP') + 1:df.columns.get_loc('First Name')].groupby('Player').agg(
             lambda x: cls._weighted_average(df, x))
        return df

    @classmethod
    def _team_data(cls) -> pd.DataFrame:
        """
        Method to return team data keyed by team name
        :return: pandas DataFrame
        """
        df = cls._read_csv(cls.files[TEAM])
        df.index = df.pop('Team')
        return df.loc[:, MOV:]

    @classmethod
    def _weighted_average(cls, dataframe: pd.DataFrame, player) -> float:
        """
        Returns a weighted average by minutes played to aggregate players with multiple rows
        :param dataframe: pandas.DataFrame
        :param player: DataFrame row or column
        :return: float: weighted average
        """
        try:
            return np.average(player, weights=dataframe.loc[player.index, MINUTES])
        except TypeError:
            return 0

    @abstractmethod
    def _create_dataset(self) -> pd.DataFrame:
        """
        Implement to create dataset
        :return: pandas DataFrame
        """
        raise NotImplementedError

    def _load_stat_tables(self) -> dict:
        """
        Instance method to load needed player stat tables on demand
        :return: dict: keyed by table name (str) with values of DataFrame holding table (pandas.DataFrame)
        """
        return {t: self._player_data(self.files[t]) for t in self._stat_table_names}

    def get_dataset(self) -> pd.DataFrame:
        """
        Method to hold DataFrame for repeat calls
        :return: pandas DataFrame
        """
        if self._dataframe is None:
            self._dataframe = self._create_dataset()
        return self._dataframe
