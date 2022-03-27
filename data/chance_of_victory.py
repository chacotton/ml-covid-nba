import numpy as np
import pandas as pd
from data import Dataset
from data.constants import *
from collections import defaultdict
from importlib import import_module
from functools import partial


class WinDataset(Dataset):

    players = [f'Player_{x}' for x in range(15)]

    def __init__(self, problem="classification", stats="all", optimize=False):
        assert problem in [CLASSIFICATION, REGRESSION], "Must be 'classification' or 'regression'"
        super().__init__()
        self.__name__ = 'Win Probability'
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
    def _return_stats(x, stats, stat_tables):
        try:
            player = x.split('/')[-1]
            out = pd.Series(dtype='float64')
            for table, stats in stats.items():
                out = pd.concat([out, stat_tables[table].loc[player, stats]])
        except (KeyError, AttributeError):
            out = pd.Series([np.nan])
        return out

    def _target(self, dataframe):
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

    def _game_dataset(self, dataframe):
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
        return dataframe

    def _create_dataset(self):
        df = self._read_csv(self.files[GAMES])
        task = self._target(df.loc[:, :HOME])
        metrics = self._game_dataset(df.loc[:, PLAYER:])
        if self.regression:
            team_df = self._team_data()
            team_df = task.Opponent.apply(lambda team: team_df.loc[team, :]).add_prefix('Opponent_')
            metrics = pd.concat([metrics.reset_index(drop=True), team_df.reset_index(drop=True)], axis=1)
        return pd.concat([task.reset_index(drop=True), metrics.reset_index(drop=True)], axis=1)


if __name__ == '__main__':
    df = WinDataset(problem='classification', optimize=True).get_dataset()
    print(df.head(10))
