"""
Main Module that handles collection of data, transformations, and table writing
"""
import datetime
import argparse
from functools import partial
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from data_ingestion.db_utils import read_table, write_db, get_engine
from basketball_reference_scraper.box_scores import get_box_scores
from basketball_reference_scraper.teams import get_team_ratings
from data_ingestion.constants import TEAMS
from data_ingestion.injury_labeller.injuryScore import InjuryScore
from data_ingestion.stat_utils import *

games_today = "SELECT GAME_DATE, HOME, AWAY FROM NBA.SCHEDULE WHERE GAME_DATE = :today"
active_players = "select player_id from ACTIVE_ROSTER_DUMMY where GAME_DATE = :game_date and ACTIVE = 1"
pie_lookup = "select player_id, pie from PLAYER_STATS where SEASON = :season"
actives_update = "update active_roster_dummy set mp = :mp where PLAYER_ID = :player_id and GAME_DATE = :game_date"
char_replace = str.maketrans({'0': 'Z', '1': 'O', '2': 'T', '3': 'H', '%': 'P', '+': 'L', '-': 'M', '/': 'S',
                              '.': 'D', '#': 'N'})
player_to_id = "SELECT player_id, name from nba.PLAYER_IDS"


@func_timer
def update_player_stats(games: pd.DataFrame, connection: Connection) -> bool:
    names = read_table("SELECT player_id, name FROM NBA.PLAYER_IDS", index_col="player_id")
    updates = 0
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
                except (TimeoutError, AttributeError):
                    continue
                stats = {k.upper().translate(char_replace): int(v) if isinstance(v, np.int64) else v for k, v in stats.items()}
                try:
                    stats['PLAYER'] = names.loc[player, 'name']
                except (IndexError, KeyError):
                    stats['PLAYER'] = df[df.player_id == player].PLAYER[0]
                stats['PLAYER_ID'] = player
                stats['PIE'] = np.clip(InjuryScore.pie_score(df, player), .01, 1).astype(float)
                write_db('player_update.sql', connection=connection, **stats)
                updates += 1
    print(f'Player Rows Update: {updates}')
    return len(games) > 0


@func_timer
def update_team_stats(games: pd.DataFrame, connection: Connection) -> bool:
    if len(games) == 0:
        print('Team Rows Updated: 0')
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
    print(f'Team Rows Updated: {len(team_stats)}')
    return True


def update_info(game_date, id_checker, connection):
    season = game_date.year if game_date.month < 7 else game_date.year + 1
    players = read_table(active_players, game_date=game_date)
    if players.empty:
        print(f'Roster Rows Updated: 0')
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
    print(f'Roster Rows Updated: {len(df[df.player_id.isin(players.player_id)])}')


def add_new_players(game_date, id_checker, connection):
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
    if actives.empty:
        print('No New Roster Rows Added')
        return
    actives.team = actives.team.apply(lambda x: {'LA Clippers': 'Los Angeles Clippers'}.get(x, x))
    season = game_date.year if game_date.month < 7 else game_date.year + 1
    distances = {team: read_table('dist.sql',
                                  team=team,
                                  target_date=game_date,
                                  date_range=game_date - datetime.timedelta(days=5),
                                  season=season,
                                  index_col='game_date').loc[game_date, 'dist'] for team in actives.team.unique()}
    actives['distance'] = actives.apply(lambda row: distances[row.team] if row.active else 0, axis=1)
    actives['season'], actives['game_date'] = [season, game_date]
    actives = actives[actives.player_id.notna()].fillna(0)
    success, failed = 0, 0
    for i, row in actives.iterrows():
        try:
            write_db('roster_update.sql', connection=connection, **row)
            success += 1
        except IntegrityError:
            failed += 1
    print(f'New Roster Rows\nAdded:  {success}\nFailed: {failed}')


@func_timer
def update_roster(day, connection: Connection = None) -> bool:
    ids = read_table(player_to_id, index_col='name')
    id_checker = partial(id_check, ids=ids)
    update_info(day, id_checker, connection)
    add_new_players(day + datetime.timedelta(days=1), id_checker, connection)
    return len(games) > 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Database Updater")
    parser.add_argument('-p', '--player', action='store_true')
    parser.add_argument('-t', '--team', action='store_true')
    parser.add_argument('-r', '--roster', action='store_true')
    parser.add_argument('-d', '--date', type=str, help='date in format YYYY-MM-DD or csv file')
    args = parser.parse_args()

    if args.date is None:
        today = datetime.date.today()
    elif args.date.endswith('.csv'):
        today = pd.read_csv(args.date, parse_dates=['game_date']).loc[0, 'game_date'] - datetime.timedelta(days=1)
    else:
        today = datetime.datetime.strptime(args.date, '%Y-%m-%d')

    games = read_table(games_today, today=today)
    with get_engine().begin() as conn:
        if args.player:
            update_player_stats(games, conn)
        if args.team:
            update_team_stats(games, conn)
        if args.roster:
            update_roster(today, conn)

