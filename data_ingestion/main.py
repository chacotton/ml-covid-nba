"""
Main Module that handles collection of data, transformations, and table writing
"""
import datetime
import numpy as np
import pandas as pd
from sqlalchemy.engine import Connection
from data_ingestion.db_utils import read_table, write_db, timeout, get_engine
from basketball_reference_scraper.box_scores import get_box_scores
from basketball_reference_scraper.teams import get_team_ratings
from data_ingestion.constants import TEAMS
from data_ingestion.injury_labeller.injuryScore import InjuryScore
from data_ingestion.stat_utils import join_player_stats, is_active

games_today = "SELECT GAME_DATE, HOME, AWAY FROM NBA.SCHEDULE WHERE GAME_DATE = :today"
char_replace = str.maketrans({'0': 'Z', '1': 'O', '2': 'T', '3': 'H', '%': 'P', '+': 'L', '-': 'M', '/': 'S',
                              '.': 'D', '#': 'N'})


def update_player_stats(games: pd.DataFrame, connection: Connection) -> bool:
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
                write_db('player_update.sql', connection=connection, **stats)
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

