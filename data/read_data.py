import pandas as pd
import numpy as np
from data import *
from pathlib import Path

covid_values = ['health and safety', 'COVID']
covid = '|'.join(covid_values)
covid_cols = ['Acquired', 'Relinquished']


def read_data(name: str) -> pd.DataFrame:
    """Import this function

    Call with String variables in __init__
    example
    from data import COVID
    from data.read_data import read_data
    read_data(COVID)
    returns a dataframe based on file selection
    """
    df = pd.read_csv(Path(__file__).parent / files[name].folder / files[name].file)
    if 'player_data/' == files[name].folder:
        df[['Player', 'First Name', 'Last Name']] = df.apply(lambda row: _split_player_name(row.Player),
                                                             result_type='expand', axis=1)
    elif 'covid_data/' == files[name].folder:
        df = df.assign(
            **{'Player': df['Acquired'].fillna(df['Relinquished'])}
        ).drop(covid_cols, axis=1)
        df['Player'] = df['Player'].apply(lambda name: name.split(' ', 1)[1].split('/', 1)[0].strip())
        new_df = df.apply(lambda x: _covid_data(x), axis=1, result_type='expand').dropna(axis=0)
        new_df.set_axis(['Player', 'Team', 'Deactivated'], axis=1, inplace=True)
        dfs = dict(tuple(df.groupby('Player')))
        new_df['Activated'] = new_df.apply(lambda row: _return_to_play(row, dfs), axis=1)
        df = new_df.dropna(axis=0)
    return df


def _return_to_play(row, dfs):
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


def _covid_data(row):
    if any(c in row.Notes for c in covid_values):
        return row.Player, row.Team, row.Date
    else:
        return np.nan, np.nan, np.nan


def _split_player_name(name: str):
    player, first, last = "", "", ""
    name = name.split(' ', 1)
    first = name[0]
    last, player = name[-1].split('\\', 1)
    return player, first, last


if __name__ == '__main__':
    data = read_data(COVID)
    print(data.head())