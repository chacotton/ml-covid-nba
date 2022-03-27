from data import Dataset
from data.constants import *
import pandas as pd
import numpy as np


class Covid(Dataset):
    """
    Class to create and store Covid Recovery Dataset

    Covid Dataset:
    """

    covid_values = ['health and safety', 'COVID']
    covid = '|'.join(covid_values)
    covid_cols = ['Acquired', 'Relinquished']

    def __init__(self):
        """
        Initialization method
        """
        super().__init__(name='Covid Recovery')
        self.files = {
            **self.files,
            COVID: self.DataFile('covid_data/', 'NBA_Injury_Data.csv')
        }

    @staticmethod
    def _return_to_play(row, dfs: pd.DataFrame) -> str:
        """
        Helper method to apply to covid injury dataframe
        :param row: row of pandas DataFrame
        :param dfs: pd.DataFrame: DataFrame of Injury data
        :return: str: Date of Activation
        """
        df = dfs[row.Player].reset_index()
        out = df[df.Date == row.Deactivated].index[0]
        try:
            status = df.iloc[out + 1, :]
        except IndexError:
            return np.nan
        if 'activated' in status.Notes:
            return status.Date
        else:
            return np.nan

    @classmethod
    def _covid_data(cls, row) -> tuple:
        """
        Helper method to split string into player, team, date
        :param row: DataFrame row
        :return: tuple of strs or np.nan if invalid row
        """
        if any(c in row.Notes for c in cls.covid_values):
            return row.Player, row.Team, row.Date
        else:
            return np.nan, np.nan, np.nan

    def _covid_dataset(self) -> pd.DataFrame:
        """
        Method to create a DataFrame of a player's covid deactivation
        :return: pandas.DataFrame of when a player got COVID-19 and when they returned
        """
        df = self._read_csv(self.files[COVID])
        df = df.assign(
            **{'Player': df['Acquired'].fillna(df['Relinquished'])}
        ).drop(self.covid_cols, axis=1)
        df['Player'] = df['Player'].apply(lambda name: name.split(' ', 1)[1].split('/', 1)[0].strip())
        new_df = df.apply(lambda x: self._covid_data(x), axis=1, result_type='expand').dropna(axis=0)
        new_df.set_axis(['Player', 'Team', 'Deactivated'], axis=1, inplace=True)
        dfs = dict(tuple(df.groupby('Player')))
        new_df['Activated'] = new_df.apply(lambda row: self._return_to_play(row, dfs), axis=1)
        return new_df.dropna(axis=0)

    def _create_dataset(self) -> pd.DataFrame:
        """
        Implements abstract method to create dataset
        :return: pandas.DataFrame
        """
        return self._covid_dataset()


if __name__ == '__main__':
    df = Covid().get_dataset()
    print(df.head(10))
