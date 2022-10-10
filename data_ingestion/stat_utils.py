import pandas as pd
import numpy as np
from datetime import date
from nba_api.stats.endpoints import playergamelogs
from nba_api.live.nba.endpoints import boxscore
from basketball_reference_scraper.players import get_stats
from data_ingestion.db_utils import timeout
import warnings
warnings.filterwarnings('ignore')


stat_tables = ['ADVANCED', 'PER_GAME', 'ADJ_SHOOTING', 'PBP', 'SHOOTING']
shooting_cols = ['SEASON', 'AGE', 'TEAM', 'LEAGUE', 'POS', 'G', 'FG%', 'Dist', '2P_FGA%', '0-3FT_FGA%', '3-10_FGA%',
                 '10-16FT_FGA%', '16-3PFT_FGA%', '3P_FGA%', '2P_FG%', '0-3_FG%', '3-10_FG%', '10-16_FG%', '16-3P_FG%',
                 '3P_FG%', '2P_FG_AST%', '3P_FG_AST%', '%FGA_DUNK', '#_DUNK', '%3PA', '3P%', 'Att_Heave', '#_Heave']
pbp_base_cols = {'PG%': 6, 'SG%': 7, 'SF%': 8, 'PF%': 9, 'C%': 10}
pbp_cols = ['SEASON', 'AGE', 'TEAM', 'LEAGUE', 'POS', 'G', 'PE_PG%', 'PE_SG%', 'PE_SF%',
            'PE_PF%', 'PE_C%', '+/-_OnCourt', '+/-_On-Off', 'TO_BadPass', 'TO_LostBall', 'Shoot_FL_COM',
            'Off._FL_COM', 'Shoot_FL_DRN', 'Off._FL_DRN', 'PGA', 'And1', 'Blkd']


def join_player_stats(player_id: str, year: int) -> pd.DataFrame:
    df = get_stats(player_id, stat_type=stat_tables[0]).dropna(axis=1, how='all')
    for stat in stat_tables[1:]:
        new_df = timeout(10, get_stats, func_args=(player_id, stat)).drop(['MP'], axis=1)
        new_df = new_df.loc[:, ~new_df.columns.str.match('Unnamed')]
        if not pd.api.types.is_numeric_dtype(new_df.G):
            new_df = new_df[~new_df.G.str.contains('Did Not Play')]
            new_df.loc[:, 'G':] = new_df.loc[:, 'G':].astype(float)
        if stat == stat_tables[-1]:
            new_df.columns = shooting_cols
            new_df.drop(['3P%'], axis=1, inplace=True)
        if stat == stat_tables[-2]:
            for c in pbp_base_cols:
                new_df[c] = new_df[c].apply(lambda x: float(x.rstrip('%'))/100 if '%' in str(x) else x)
            new_df.columns = pbp_cols
        new_df = new_df.loc[:, ~new_df.columns.duplicated()]
        if stat == stat_tables[2]:
            df.drop(['FG', '2P', '3P', 'FT'], axis=1, inplace=True)
        df = df.merge(new_df)
    df.columns = [c.replace(' ', "_") for c in df.columns]
    df['EFG'] = df['eFG%']
    df.drop(['GS', 'LEAGUE'], axis=1, inplace=True)
    df.replace([np.nan], [None], inplace=True)
    return df.loc[df.SEASON == year]


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


if __name__ == '__main__':
    print(is_injured(date(2022,1,28)))