import time
import pandas as pd
import numpy as np
from datetime import date
from nba_api.stats.endpoints import playergamelogs
from nba_api.live.nba.endpoints import boxscore
import requests
from bs4 import BeautifulSoup, Comment
import warnings
warnings.filterwarnings('ignore')


stat_tables = ['ADVANCED', 'PER_GAME', 'ADJ_SHOOTING', 'PBP', 'SHOOTING']
shooting_cols = ['Player', 'Pos', 'Age', 'Tm', 'G', 'FG%', 'Dist', '2P_FGA%', '0-3FT_FGA%', '3-10_FGA%',
                 '10-16FT_FGA%', '16-3PFT_FGA%', '3P_FGA%', '2P_FG%', '0-3_FG%', '3-10_FG%', '10-16_FG%', '16-3P_FG%',
                 '3P_FG%', '2P_FG_AST%', '3P_FG_AST%', '%FGA_DUNK', '#_DUNK', '%3PA', '3P%', 'Att_Heave', '#_Heave']
pbp_base_cols = {'PG%': 6, 'SG%': 7, 'SF%': 8, 'PF%': 9, 'C%': 10}
pbp_cols = ['Player', 'Pos', 'Age', 'Tm', 'G', 'PE_PG%', 'PE_SG%', 'PE_SF%',
            'PE_PF%', 'PE_C%', '+/-_OnCourt', '+/-_On-Off', 'TO_BadPass', 'TO_LostBall', 'Shoot_FL_COM',
            'Off._FL_COM', 'Shoot_FL_DRN', 'Off._FL_DRN', 'PGA', 'And1', 'Blkd']

stat_tables_dict = {
    'ADVANCED': ('advanced', 'advanced'),
    'PER_GAME': ('per_game', 'per_game'),
    'ADJ_SHOOTING': ('adj_shooting', 'adj-shooting'),
    'PBP': ('play-by-play', 'pbp'),
    'SHOOTING': ('shooting', 'shooting'),
}


def get_stats(stat_table, year):
    url = f'https://www.basketball-reference.com/leagues/NBA_{year}_{stat_tables_dict[stat_table][0]}.html#{stat_tables_dict[stat_table][1]}_stats'
    try:
        df = pd.read_html(url)[0]
    except ValueError:
        df = errant_table(url)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel()
    df = df[df.Rk != 'Rk']
    try:
        pids = pd.read_html(url, extract_links='all')[0].iloc[:, 1]
    except ValueError:
        pids = errant_table(url, True).iloc[:, 1]
    pids = pids.apply(lambda x: x[1].rsplit('/', 1)[-1][:-5] if x[1] is not None else None)
    df.index = pids[~pids.isna()].values
    df.dropna(axis=1, how='all', inplace=True)
    df.drop(['Rk'], axis=1, inplace=True)
    df = df[~df.index.duplicated(keep='first')]
    return df

def errant_table(url, links=False):
    links = 'all' if links else None
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for each in comments:
        if 'table' in each:
            try:
                table = pd.read_html(each, extract_links=links)[0]
                return table[~table.iloc[:, 0].isna()]
            except:
                continue


def join_player_stats(player_id: str, year: int) -> pd.DataFrame:
    #df = timeout(10, get_stats, func_args=(player_id, stat_tables[0])).dropna(axis=1, how='all')
    df = get_stats(stat_tables[0], year)
    df.loc[:, 'G':] = df.loc[:, 'G':].astype(float)
    for stat in stat_tables[1:]:
        #new_df = timeout(10, get_stats, func_args=(player_id, stat)).drop(['MP'], axis=1)
        new_df = get_stats(stat, year).drop(['MP'], axis=1)
        new_df = new_df.loc[:, ~new_df.columns.str.match('Unnamed')]
        if not pd.api.types.is_numeric_dtype(new_df.G):
            new_df = new_df[~new_df.G.str.contains('Did Not Play')]
        if stat == stat_tables[-1]:
            new_df.columns = shooting_cols
            new_df.drop(['3P%'], axis=1, inplace=True)
        if stat == stat_tables[-2]:
            for c in pbp_base_cols:
                new_df[c] = new_df[c].apply(lambda x: float(x.rstrip('%'))/100 if '%' in str(x) else x)
            new_df.columns = pbp_cols
        new_df.loc[:, 'G':] = new_df.loc[:, 'G':].astype(float)
        new_df = new_df.loc[:, ~new_df.columns.duplicated()]
        if stat == stat_tables[2]:
            df.drop(['FG', '2P', '3P', 'FT'], axis=1, inplace=True)
        df = pd.merge(df, new_df, left_index=True, right_index=True)
        df.columns = [c[:-2] if c.endswith('_x') or c.endswith('_y') else c for c in df.columns]
        df = df.loc[:, ~df.columns.duplicated()]
    df.columns = [c.replace(' ', "_") for c in df.columns]
    df['EFG'] = df['eFG%']
    df.drop(['GS', 'Tm'], axis=1, inplace=True)
    df.replace([np.nan], [None], inplace=True)
    return df


def is_active(day: date, player: str):
    curr_season = day.year if day.month < 7 else day.year + 1
    c = playergamelogs.PlayerGameLogs(
        season_nullable=f'{curr_season - 1}-{curr_season % 100}',
        date_from_nullable=day.strftime('%m/%d/%Y'),
        date_to_nullable=day.strftime('%m/%d/%Y')
    ).player_game_logs.get_data_frame()
    return c

#return dictionary of status on a given day
#covid key value denoted as 'INACTIVE_HEALTH_AND_SAFETY_PROTOCOLS'
def is_injured(day: date):
    df = pd.DataFrame(columns=['player', 'team', 'status'])
    curr_season = day.year if day.month < 7 else day.year + 1
    c = playergamelogs.PlayerGameLogs(
        season_nullable=f'{curr_season - 1}-{curr_season % 100}',
        date_from_nullable=day.strftime('%m/%d/%Y'),
        date_to_nullable=day.strftime('%m/%d/%Y')
    ).player_game_logs.get_data_frame()
    games = set(c['GAME_ID'].tolist())
    for game in games:
        box = boxscore.BoxScore(game)
        home = box.home_team_player_stats.get_dict()
        home_team = f'{box.home_team.get_dict()["teamCity"]} {box.home_team.get_dict()["teamName"]}'
        away = box.away_team_player_stats.get_dict()
        away_team = f'{box.away_team.get_dict()["teamCity"]} {box.away_team.get_dict()["teamName"]}'
        for team, players in zip((home_team, away_team), (home, away)):
            for p in players:
                d = {'player': p['firstName'] + " " + p['familyName'],
                     'team': team,
                     'status': None}
                if p['status'] == 'ACTIVE':
                    d['status'] = 'ACTIVE'
                elif 'notPlayingReason' in p:
                    d['status'] = p['notPlayingReason']
                df = df.append(d, ignore_index=True)
    return df


def split_status(status):
    active = 1
    covid = 0
    if status is None:
        active = 0
    elif status != 'ACTIVE':
        status = status.split('_', 1)
        active = 0
        if status[-1] == 'HEALTH_AND_SAFETY_PROTOCOLS':
            covid = 1
    return active, covid


def id_check(name, ids):
    name = name.replace('.', '')
    if name.endswith(('Jr', 'III', 'IV')):
        name = name.rsplit(' ', 1)[0]
    if name in ids.index:
        player_id = ids.loc[name, 'player_id']
        if isinstance(player_id, str):
            return player_id
        else:
            return player_id[-1]
    else:
        name = name.split(' ')
        first, last = name[0], name[1]
        potential_id = last.lower()[:5] + first.lower()[:2]
        try:
            return ids[ids.player_id.str.startswith(potential_id, na=False)].iloc[-1, 0]
        except IndexError:
            return None


def pie_score(player, team):
    def func(d):
        return d['PTS'] + d['FGM'] + d['FTM'] - d['FGA'] - d['FTA'] + d['DREB'] + d['OREB']/2 + d['AST'] + d['STL'] + d['BLK']/2 - d['PF'] - d['TOV']
    return func(player) / func(team)


def func_timer(logger):
    def decorator(func):
        def method(*args, **kwargs):
            start = time.time()
            output = func(*args, **kwargs)
            runtime = int(time.time() - start)
            logger.info(f'Total Time: {runtime // 3600:02}:{runtime % 3600 // 60:02}:{runtime % 60:02}')
            return output
        return method
    return decorator

