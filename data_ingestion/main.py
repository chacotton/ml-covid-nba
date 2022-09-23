"""
Main Module that handles collection of data, transformations, and table writing
"""
import datetime
import numpy as np
import pandas as pd
from sqlalchemy.engine import Connection
from data_ingestion.utils import read_table, write_db, timeout, get_engine
from basketball_reference_scraper.box_scores import get_box_scores
from basketball_reference_scraper.players import get_stats
from basketball_reference_scraper.teams import get_team_ratings
from data_ingestion.constants import TEAMS
from data_ingestion.injury_labeller.injuryScore import InjuryScore

games_today = "SELECT GAME_DATE, HOME, AWAY FROM NBA.SCHEDULE WHERE GAME_DATE = :today"
stat_tables = ['ADVANCED', 'PER_GAME', 'ADJ_SHOOTING', 'PBP', 'SHOOTING']
shooting_cols = ['SEASON', 'AGE', 'TEAM', 'LEAGUE', 'POS', 'G', 'FG%', 'Dist', '2P_FGA%', '0-3FT_FGA%', '3-10_FGA%',
                 '10-16FT_FGA%', '16-3PFT_FGA%', '3P_FGA%', '2P_FG%', '0-3_FG%', '3-10_FG%', '10-16_FG%', '16-3P_FG%',
                 '3P_FG%', '2P_FG_AST%', '3P_FG_AST%', '%FGA_DUNK', '#_DUNK', '%3PA', '3P%', 'Att_Heave', '#_Heave']
pbp_base_cols = {'PG%': 6, 'SG%': 7, 'SF%': 8, 'PF%': 9, 'C%': 10}
pbp_cols = ['SEASON', 'AGE', 'TEAM', 'LEAGUE', 'POS', 'G', 'PE_PG%', 'PE_SG%', 'PE_SF%',
            'PE_PF%', 'PE_C%', '+/-_OnCourt', '+/-_On-Off', 'TO_BadPass', 'TO_LostBall', 'Shoot_FL_COM',
            'Off._FL_COM', 'Shoot_FL_DRN', 'Off._FL_DRN', 'PGA', 'And1', 'Blkd']
char_replace = str.maketrans({'0': 'Z', '1': 'O', '2': 'T', '3': 'H', '%': 'P', '+': 'L', '-': 'M', '/': 'S',
                              '.': 'D', '#': 'N'})


def join_player_stats(player_id: str, year: int) -> pd.DataFrame:
    df = get_stats(player_id, stat_type=stat_tables[0]).dropna(axis=1)
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


def update_player_stats(games: pd.DataFrame, connecion: Connection) -> bool:
    names = read_table("SELECT player_id, name FROM NBA.PLAYER_IDS", index_col="player_id")
    for _, game in games.iterrows():
        dfs = timeout(10, get_box_scores, attempts=3, func_args=(game.game_date, TEAMS[game.home], TEAMS[game.away]))
        for team in [game.home, game.away]:
            df = dfs[TEAMS[team]]
            df.MP = df.MP.apply(lambda x: int(x.split(':')[0]) if len(x.split(':')) > 1 else 0)
            player_ids = df[df.MP > 0].player_id.values
            for player in player_ids:
                year = game.game_date.year if game.game_date.month < 7 else game.game_date.year + 1
                try:
                    stats = join_player_stats(player, year).iloc[0, :]
                except TimeoutError:
                    continue
                stats = {k.upper().translate(char_replace): int(v) if isinstance(v, np.int64) else v for k, v in stats.items()}
                try:
                    stats['PLAYER'] = names.loc[player, 'name']
                except IndexError:
                    stats['PLAYER'] = df[df.player_id == player].PLAYER[0]
                stats['PLAYER_ID'] = player
                stats['PIE'] = InjuryScore.pie_score(df, player)
                write_db('player_update.sql', connection=connecion, **stats)
    return len(games) > 0


def update_team_stats(games: pd.DataFrame, connection: Connection) -> bool:
    if len(games) == 0:
        return False
    teams = games.home.to_list() + games.away.to_list()
    teams = [TEAMS[t] for t in teams]
    year = games.loc[0, 'game_date'].year if games.loc[0, 'game_date'].month < 7 else games.loc[0, 'game_date'].year + 1
    team_stats = get_team_ratings(team=teams, season_end_year=year)
    team_stats.SEASON = year
    team_stats.TEAM = team_stats.TEAM.map({v: k for k, v in TEAMS.items()})
    for _, row in team_stats.iterrows():
        stats = {k.upper().translate(char_replace): int(v) if isinstance(v, np.int64) else v for k, v in row.items()}
        write_db('team_update.sql', connection=connection, **stats)
    return True


def update_roster(games: pd.DataFrame, connection: Connection) -> bool:
    return len(games) > 0


if __name__ == '__main__':
    PLAYER, TEAM, ROSTER = False, True, False
    today = datetime.date(2022, 1, 10)
    games = read_table(games_today, today=today)
    with get_engine().begin() as conn:
        if PLAYER:
            update_player_stats(games, conn)
        if TEAM:
            update_team_stats(games, conn)
        if ROSTER:
            update_roster(games, conn)

