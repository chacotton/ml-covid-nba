import numpy as np
import pandas as pd
from data_ingestion import Dataset
from data_ingestion.constants import *
from collections import defaultdict
from importlib import import_module
from functools import partial
from itertools import chain, product


class WinDataset(Dataset):
    """
    Class to create and return Chance of Victory Dataset

    Creates two types of datasets, classification and regression
    Classification:
        Outcome column: 0 - Away team won, 1 - Home team won
        Other columns contain stats for all players active in game
    Regression:
        Team column: name of team for which points are shown
        Team_pts column: points scored by team
        Opponent column: name of opponent
        Player columns: stats for each player on team
        Opponent columns: team stats for opponent
    * All empty values are encoded as np.nan
    """

    players = [f'Player_{x}' for x in range(15)]

    def __init__(self, problem: str = "classification", stats: list = "all", optimize: bool = False):
        """
        Initialization function for win probability dataset
        :param problem: str: default='classification', must be 'classification' or 'regression'
        :param stats: default='all' or list of str with statistics to use (invalid stats will be ignored)
        :param optimize: default = False, whether to use multiprocessing for creating dataset
        :raises: AssertionError: raised if invalid problem passed
        """

        assert problem in [CLASSIFICATION, REGRESSION], "Must be 'classification' or 'regression'"
        super().__init__(name='Win Probability')
        self.classification = problem == CLASSIFICATION
        self.regression = problem == REGRESSION
        if stats == 'all':
            self.stats = STATS
        else:
            self.stats = {k: v for k, v in STATS if k in stats}
        stats = defaultdict(list)
        for k, v in self.stats.items():
            stats[v].append(k)
        self.stats = stats
        self._stat_table_names = self.stats.keys()
        self._stat_tables = None
        self.files = {
            **self.files,
            'games': self.DataFile('team_data/', 'NBA_games_21-22.csv'),
        }
        self.optimize = optimize
        if self.optimize:
            try:
                pandarallel = getattr(import_module('pandarallel'), 'pandarallel')
                pandarallel.initialize()
            except ModuleNotFoundError:
                self.optimize = False
                print("Pandarallel must be installed to use multiprocessing performance improvements\n"
                      "'pip install pandarallel' to install")

    @staticmethod
    def _return_stats(x, stats: dict, stat_tables: dict):
        """
        Helper method to return stats by player
        :param x: item in pandas DataFrame
        :param stats: self.stats
        :param stat_tables: self._stat_tables
        :return: pandas.Series: Series of player stats
        """
        try:
            player = x.split('/')[-1]
            out = pd.Series(dtype='float64')
            for table, stats in stats.items():
                out = pd.concat([out, stat_tables[table].loc[player, stats]])
        except (KeyError, AttributeError):
            out = pd.Series([np.nan])
        return out

    def _target(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Method to return target columns
        :param dataframe: columns relevant to creating target column
        :return: pandas.DataFrame: target column(s)
        """
        if self.classification:
            dataframe['Outcome'] = dataframe.apply(lambda x: 1 if x.Home_pts > x.Away_pts else 0, axis=1)
            dataframe = dataframe.loc[:, 'Outcome':]
        elif self.regression:
            new_df = dataframe.loc[:, ['Away', 'Away_pts', 'Home']]
            new_df.rename({'Away': 'Team', 'Away_pts': 'Points', 'Home': 'Opponent'}, axis=1, inplace=True)
            new_df['Location'] = 'Away'
            dataframe = dataframe.loc[:, ['Home', 'Home_pts', 'Away']]
            dataframe.rename({'Home': 'Team', 'Home_pts': 'Points', 'Away': 'Opponent'}, axis=1, inplace=True)
            dataframe['Location'] = 'Home'
            dataframe = pd.concat([dataframe, new_df], axis=0)
        return dataframe

    def _game_dataset(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Method to return player statistics dataframe
        :param dataframe: pandas.DataFrame with players to get stats for
        :return: pandas.DataFrame
        """
        self._stat_tables = self._load_stat_tables()
        return_stats = partial(self._return_stats, stats=self.stats, stat_tables=self._stat_tables)
        if self.regression:
            df_1 = dataframe.loc[:, PLAYER:AWAY_END].set_axis(self.players, axis=1)
            df_2 = dataframe.loc[:, HOME_START:].set_axis(self.players, axis=1)
            dataframe = pd.concat([df_2, df_1], axis=0)
        dataframe = getattr(dataframe, f'{"parallel_" if self.optimize else ""}applymap')(return_stats)
        dataframe = pd.concat(
            [pd.DataFrame(dataframe[col].to_list()).add_prefix(col + '_') for col in dataframe.columns],
            axis=1).dropna(axis=1, how='all')
        self._stat_tables = None
        stats = chain.from_iterable(self.stats.values())
        prefix = ['Home_', 'Away_'] if self.classification else ['']
        df = pd.DataFrame()
        for i, j in product(prefix, stats):
            df[f'{i}{j}'] = dataframe[dataframe.columns[dataframe.columns.str.startswith(i) & dataframe.columns.str.endswith(j)]].sum(
                axis=1)
        return df

    def _create_dataset(self) -> pd.DataFrame:
        """
        Returns desired dataset
        :return: pandas.DataFrame
        """
        df = self._read_csv(self.files[GAMES])
        task = self._target(df.loc[:, :HOME])
        metrics = self._game_dataset(df.loc[:, PLAYER:])
        if self.regression:
            team_df = self._team_data()
            team_df = task.Opponent.apply(lambda team: team_df.loc[team, :]).add_prefix('Opponent_')
            metrics = pd.concat([metrics.reset_index(drop=True), team_df.reset_index(drop=True)], axis=1)
        return pd.concat([task.reset_index(drop=True), metrics.reset_index(drop=True)], axis=1).fillna(0)


if __name__ == '__main__':
    df = WinDataset(problem='regression', optimize=True).get_dataset()
    print(df.head(10))
