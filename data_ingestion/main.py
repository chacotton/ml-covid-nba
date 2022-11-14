"""
Main Module that handles collection of data, transformations, and table writing
"""
import datetime
import argparse
import pandas as pd
import numpy as np
import logging
import sys
import pathlib
from functools import partial
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from data_ingestion.db_utils import read_table, write_db, get_engine, timeout
from basketball_reference_scraper.box_scores import get_box_scores
from basketball_reference_scraper.teams import get_team_ratings
from data_ingestion.constants import *
from data_ingestion.injury_labeller.injuryScore import InjuryScore
from data_ingestion.stat_utils import func_timer, join_player_stats, is_active, is_injured, pie_score, split_status, id_check
from data_ingestion.bball_ref import InjuryReport
import time
from urllib.error import HTTPError

base_path = pathlib.Path('/mnt/ml-nba/logs')
logger = logging.getLogger("data_ingestion")
logger.handlers.clear()
if base_path.exists():
    time_format = datetime.datetime.now().strftime('%Y-%m-%d:%H:%M:%S')
    file_handler = logging.FileHandler(base_path / pathlib.Path(f'{time_format}_data_ingestion.log'))
    file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
    logger.addHandler(file_handler)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)


@func_timer(logger)
def update_player_stats(games: pd.DataFrame, connection: Connection) -> bool:
    """
    Updates rows of player stats by year
    :param games: pd.DataFrame of games
    :param connection: sqlalchemy connection object
    :return: boolean, whether any rows were updated
    """
    updates = 0
    player_id_list = []
    pies = []
    if len(games) > 0:
        year = games.loc[0, 'game_date'].year if games.loc[0, 'game_date'].month < 7 else games.loc[0, 'game_date'].year + 1
        all_stats = join_player_stats('', year)
        for i, game in games.iterrows():
            while True:
                try:
                    dfs = get_box_scores(game.game_date, TEAMS[game.home], TEAMS[game.away])
                    logger.info(f'Completed {i+1}/{len(games)}')
                    #dfs = timeout(10, get_box_scores, attempts=3, func_args=(game.game_date, TEAMS[game.home], TEAMS[game.away]))
                    for team in [game.home, game.away]:
                        df = dfs[TEAMS[team]]
                        df.MP = df.MP.apply(lambda x: int(x.split(':')[0]) if len(x.split(':')) > 1 else 0)
                        player_ids = df[df.MP > 0].player_id.values
                        player_id_list += [player for player in player_ids]
                        pies += [np.clip(InjuryScore.pie_score(df, player), .01, 1) for player in player_ids]
                    break
                except TimeoutError:
                    logger.warning('Basketball Reference Timed Out! Rows NOT updated')
                    return False
                except:
                    time.sleep(300)
                    continue

        all_stats = all_stats.loc[player_id_list, :]
        for _, player in all_stats.iterrows():
            stats = {k.upper().translate(char_replace): int(v) if isinstance(v, np.int64) else v for k, v in player.items()}
            stats['PLAYER_ID'] = player.name
            stats['PIE'] = pd.Series(pies, index=player_id_list)[player.name].astype(float)
            stats['SEASON'] = year
            write_db('player_update.sql', connection=connection, **stats)
            updates += 1
    logger.info(f'Player Rows Update: {updates}')
    return len(games) > 0


@func_timer(logger)
def update_team_stats(games: pd.DataFrame, connection: Connection) -> bool:
    """
    Updates Team Stat Rows by year
    :param games: pd.DataFrame of games
    :param connection: sqlalchemy connection object
    :return: boolean whether any rows were updated
    """
    if len(games) == 0:
        logger.info('Team Rows Updated: 0')
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
    logger.info(f'Team Rows Updated: {len(team_stats)}')
    return True


def update_info(game_date: datetime.date, id_checker, connection: Connection):
    """
    Updates columns in active roster based on available labels
    :param game_date: date object
    :param id_checker: function
    :param connection: sqlalchemy connection
    :return: None
    """
    season = game_date.year if game_date.month < 7 else game_date.year + 1
    players = read_table(active_players, game_date=game_date)
    if players.empty:
        logger.info('Roster Rows Updated: 0')
        return
    base_pie = read_table(pie_lookup, season=season, index_col='player_id')
    actives = is_active(game_date, '')
    teams = {team: actives[actives.TEAM_NAME == team].sum() for team in actives.TEAM_NAME.unique()}
    actives['pie'] = actives.apply(lambda row: pie_score(row, teams[row.TEAM_NAME]), axis=1)
    df = actives[['PLAYER_NAME', 'MIN', 'pie']].fillna(0)
    df.columns = ['player', 'mp', 'health']
    df.mp = df.mp.astype(int)
    df['player_id'] = df.player.apply(id_checker)
    df.health = df.apply(lambda row: np.clip(row.health / base_pie.loc[row.player_id, 'pie'], .01, 1) if row.player_id in base_pie.index else .01, axis=1).astype(float)
    for i, row in df[df.player_id.isin(players.player_id)].iterrows():
        write_db(actives_update, mp=row.mp, game_date=game_date, player_id=row.player_id, connection=connection)
    logger.info(f'Roster Rows Updated: {len(df[df.player_id.isin(players.player_id)])}')


def add_new_players(game_date: datetime.date, id_checker, connection: Connection):
    """
    Adds new players to active roster
    :param game_date: dat object
    :param id_checker: function
    :param connection: sqlalchemy connection
    :return: None
    """
    if game_date.date() == datetime.date.today():
        games = read_table(games_today, today=game_date)
        live_injury_report = InjuryReport()
        actives = []
        for team in games.home.to_list() + games.away.to_list():
            while True:
                try:
                    actives.append(live_injury_report.team_actives(team))
                    break
                except HTTPError:
                    time.sleep(300)
                    continue
        #actives = [live_injury_report.team_actives(team) for team in games.home.to_list() + games.away.to_list()]
        actives = pd.concat(actives, ignore_index=True)
        inactives = live_injury_report.injury_mapping[live_injury_report.injury_mapping.Status == 'Out']
        inactives['mp'], inactives['health'], inactives['active'] = [0, 0, 0]
        inactives['covid'] = inactives.Injury.apply(lambda x: int('health and safety' in x.lower() or x.lower().startswith('covid')))
        inactives = inactives[['Player', 'Team', 'mp', 'health', 'active', 'covid']].reset_index()
        inactives.rename({'Player': 'player', 'Team': 'team'}, axis=1, inplace=True)
        actives = pd.concat((actives, inactives), ignore_index=True)
    else:
        actives = is_active(game_date, '')
        actives = actives[['PLAYER_NAME', 'TEAM_NAME', 'MIN']]
        actives.columns = ['player', 'team', 'mp']
        actives['player_id'] = actives.player.apply(id_checker)
        actives['active'], actives['covid'], actives['health'] = [1, 0, -1]
        inactives = is_injured(game_date)
        if not inactives.empty:
            inactives[['active', 'covid']] = inactives.status.apply(split_status).apply(pd.Series)
            inactives = inactives[inactives.active == 0].drop(['status'], axis=1)
            inactives['health'] = 0
            inactives['player_id'] = inactives.player.apply(id_checker)
            actives = pd.concat((actives, inactives), ignore_index=True)
        actives.team = actives.team.apply(lambda x: {'LA Clippers': 'Los Angeles Clippers'}.get(x, x))
    if actives.empty:
        logger.info('No New Roster Rows Added')
        return
    season = game_date.year if game_date.month < 7 else game_date.year + 1
    distances = {team: read_table('dist.sql',
                                  team=team,
                                  target_date=game_date,
                                  date_range=game_date - datetime.timedelta(days=5),
                                  season=season,
                                  index_col='game_date') for team in actives.team.unique()}
    actives['distance'] = actives.apply(lambda row: distances[row.team].loc[game_date, 'dist'] if row.active else 0, axis=1)
    actives['season'], actives['game_date'] = [season, game_date]
    actives = actives[actives.player_id.notna()].fillna(0)
    success, failed = 0, 0
    for i, row in actives.iterrows():
        try:
            write_db('roster_update.sql', connection=connection, **row)
            success += 1
        except IntegrityError:
            logger.warning(f'Row Already Exists in Database: PK: {row.game_date} ^ {row.player_id}')
            failed += 1
    logger.info(f'New Roster Rows\nAdded:  {success}')
    if failed > 0:
        logger.warning(f'Failed: {failed}')


@func_timer(logger)
def update_roster(day: datetime.date, connection: Connection = None) -> bool:
    """
    Updates active roster
    :param day: date object
    :param connection: sqlalchemy connection
    :return: whether function completed successfully
    """
    ids = read_table(player_to_id, index_col='name')
    id_checker = partial(id_check, ids=ids)
    update_info(day, id_checker, connection)
    while True:
        try:
            add_new_players(day + datetime.timedelta(days=1), id_checker, connection)
            break
        except HTTPError:
            logger.info('Rate Limiting Error')
            time.sleep(600)
    return True


@func_timer(logger)
def update_schedule(day: datetime.date, connection: Connection = None) -> bool:
    season = day.year if day.month < 7 else day.year + 1
    scores = pd.read_html(f'https://www.basketball-reference.com/leagues/NBA_{season}_games-{day.strftime("%B").lower()}.html#schedule',
                          index_col='Date', parse_dates=True)[0]
    scores = scores.loc[day, 'Visitor/Neutral':'PTS.1']
    scores.columns = ['VISITOR', 'VISITOR_PTS', 'HOME', 'HOME_PTS']
    for i, row in scores.iterrows():
        out = {'home': row.HOME, 'game_date': day, 'home_pts': int(row.HOME_PTS), 'away_pts': int(row.VISITOR_PTS),
               'diff': int(abs(row.HOME_PTS - row.VISITOR_PTS)),
               'winner': row.HOME if row.HOME_PTS > row.VISITOR_PTS else row.VISITOR}
        write_db(schedule_update, **out, connection=connection)
    logger.info(f"Scores Successfully Updated: {len(scores)}")
    return True

def handle_limiting_error(func, *args):
    while True:
        try:
            out = func(*args)
            return out
        except HTTPError:
            time.sleep(300)
            continue


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Database Updater")
    parser.add_argument('-p', '--player', action='store_true')
    parser.add_argument('-t', '--team', action='store_true')
    parser.add_argument('-r', '--roster', action='store_true')
    parser.add_argument('-d', '--date', type=str, help='date in format YYYY-MM-DD or csv file')
    args = parser.parse_args()

    if args.date is None:
        today = datetime.date.today() - datetime.timedelta(days=1)
    elif args.date.endswith('.csv'):
        today = pd.read_csv(args.date, parse_dates=['game_date']).loc[0, 'game_date'] - datetime.timedelta(days=1)
    else:
        today = datetime.datetime.strptime(args.date, '%Y-%m-%d') - datetime.timedelta(days=1)
    logger.info(f'Executing with Date: {today.strftime("%Y-%m-%d")}')
    games = read_table(games_today, today=today)
    wait_time = 120
    try:
        with get_engine().begin() as conn:
            handle_limiting_error(update_schedule, today)
            time.sleep(wait_time)
            if args.player:
                handle_limiting_error(update_player_stats, games, conn)
                time.sleep(wait_time)
            if args.team:
                handle_limiting_error(update_team_stats, games, conn)
                time.sleep(wait_time)
            if args.roster:
                handle_limiting_error(update_roster, today, conn)
    except ConnectionError:
        logger.error('Database Connection Failed!')

