"""
Main Module that handles collection of data, transformations, and table writing
"""
import datetime
import numpy as np
import pandas as pd
from functools import partial
from sqlalchemy.engine import Connection
from data_ingestion.db_utils import read_table, write_db, timeout, get_engine
from basketball_reference_scraper.box_scores import get_box_scores
from basketball_reference_scraper.teams import get_team_ratings
from data_ingestion.constants import TEAMS
from data_ingestion.injury_labeller.injuryScore import InjuryScore
from data_ingestion.stat_utils import join_player_stats, is_active, is_injured

games_today = "SELECT GAME_DATE, HOME, AWAY FROM NBA.SCHEDULE WHERE GAME_DATE = :today"
char_replace = str.maketrans({'0': 'Z', '1': 'O', '2': 'T', '3': 'H', '%': 'P', '+': 'L', '-': 'M', '/': 'S',
                              '.': 'D', '#': 'N'})
player_to_id = "SELECT player_id, name from nba.PLAYER_IDS"


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
    teams = {TEAMS[t] for t in teams}
    year = games.loc[0, 'game_date'].year if games.loc[0, 'game_date'].month < 7 else games.loc[0, 'game_date'].year + 1
    team_stats = get_team_ratings(team=teams, season_end_year=year)
    team_stats.SEASON = year
    team_stats.TEAM = team_stats.TEAM.map({v: k for k, v in TEAMS.items()})
    for _, row in team_stats.iterrows():
        stats = {k.upper().translate(char_replace): int(v) if isinstance(v, np.int64) else v for k, v in row.items()}
        write_db('team_update.sql', connection=connection, **stats)
    return True

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


def update_roster(games: pd.DataFrame, connection: Connection = None) -> bool:
    ids = read_table(player_to_id, index_col='name')
    id_checker = partial(id_check, ids=ids)
    day = games.game_date[0]
    #day = datetime.date(2022, 1, 5)
    actives = is_active(day, '')
    actives = actives[['PLAYER_NAME', 'TEAM_NAME']]
    actives.columns = ['player', 'team']
    actives['player_id'] = actives.player.apply(id_checker)
    actives['active'] = 1
    actives['covid'] = 0
    actives['health'] = -1
    inactives = is_injured(day)
    inactives[['active', 'covid']] = inactives.status.apply(split_status).apply(pd.Series)
    inactives = inactives[inactives.active == 0]
    inactives.drop(['status'], axis=1, inplace=True)
    inactives['health'] = 0
    inactives['player_id'] = inactives.player.apply(id_checker)
    actives = pd.concat((actives, inactives), ignore_index=True)
    actives['distance'] = -1
    actives['mp'] = 0
    actives['impact'] = -1
    actives['season'] = 2022
    actives['game_date'] = day
    return actives


if __name__ == '__main__':
    PLAYER, TEAM, ROSTER = False, False, True
    today = datetime.date(2022, 1, 5)
    games = read_table(games_today, today=today)
    with get_engine().connect() as conn:
        if PLAYER:
            update_player_stats(games, conn)
        if TEAM:
            update_team_stats(games, conn)
        if ROSTER:
            update_roster(games, conn)

