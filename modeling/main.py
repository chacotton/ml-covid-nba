import argparse
import pathlib
import logging
import sys
from sqlalchemy.engine import Connection
import pandas as pd
from datetime import date, datetime
from modeling.chance_of_victory import NBACoV
from modeling.covid_recovery import NBACovid
from modeling import func_timer
from modeling.utils import read_table, get_engine, write_db, resolve_path

base_path = pathlib.Path('/mnt/ml-nba/logs')
logger = logging.getLogger("modeling")
logger.handlers.clear()
if base_path.exists():
    time_format = datetime.datetime.now().strftime('%Y-%m-%d:%H:%M:%S')
    file_handler = logging.FileHandler(base_path / pathlib.Path(f'{time_format}_modeling.log'))
    file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
    logger.addHandler(file_handler)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

player_impact = 'select game_date, player_id, season, team, health, impact from nba.ACTIVE_ROSTER_DUMMY ' \
                'where GAME_DATE <= :game_date order by PLAYER_ID, GAME_DATE'
impact_update = 'update nba.active_roster_dummy set impact = :impact where GAME_DATE = :game_date and PLAYER_ID = :player_id'
health_calc = "SELECT player_id from ACTIVE_ROSTER_DUMMY where GAME_DATE = :today and HEALTH = -1"
health_update = "update active_roster_dummy set health = :health, PRED_HEALTH = :health where PLAYER_ID = :player_id and game_date = :game_date"
win_prob = "SELECT GAME_DATE, HOME FROM NBA.SCHEDULE WHERE GAME_DATE = :today and HOME_WIN_PROB < 0"
win_update = "update schedule set HOME_WIN_PROB = :home_win, AWAY_WIN_PROB = :away_win where GAME_DATE = :game_date and HOME = :team"


@func_timer(logger)
def calculate_impact(game_date: date, model: NBACoV, connection: Connection, season: int):
    rows = read_table(player_impact, game_date=game_date)
    rows = dict(tuple(rows.groupby('player_id')))
    impact_generated = 0
    for player_id, player_df in rows.items():
        if player_df.health.iloc[-1] == 0:
            old_health = 1
        elif len(player_df) > 2:
            old_health = player_df.health.iloc[-2]
        else:
            old_health = 0
        new_health = player_df.health.iloc[-1]
        past_df = read_table('impact_table.sql', connection=connection, season=season, game_date=game_date,
                             player_id=player_id, team=player_df.team.iloc[-1], health=float(old_health))
        new_df = read_table('impact_table.sql', connection=connection, season=season, game_date=game_date,
                            player_id=player_id, team=player_df.team.iloc[-1], health=float(new_health))
        if past_df.empty and new_df.empty:
            impact = 0
        else:
            base = model.predict(past_df.iloc[:, 3:])
            new = model.predict(new_df.iloc[:, 3:])
            if player_df.team.iloc[-1] == new_df.loc[0, 'home']:
                impact = (new - base).item()
            else:
                impact = (base - new).item()
        write_db(impact_update, impact=float(impact), game_date=game_date, player_id=player_id, connection=connection)
        impact_generated += 1
    logger.info(f'Impacts Calculated: {impact_generated}')


@func_timer(logger)
def calculate_win_prob(game_date: date, model: NBACoV, connection: Connection, season: int):
    df = model.inference_table(game_date, season)
    games = read_table(win_prob, today=game_date, connection=connection)
    wins = 0
    if len(games) > 0:
        pred = model.predict(df.iloc[:, 3:])
        for yhat, team in zip(pred.astype(float), df.home):
            if team in games.home.to_list():
                write_db(win_update, home_win=yhat, away_win=(1 - yhat), game_date=game_date, team=team, connection=connection)
                wins += 1
    logger.info(f'Games Predicted:   {wins}')


@func_timer(logger)
def calculate_health(game_date, model, connection: Connection, *args, **kwargs):
    players = read_table(health_calc, today=game_date)
    healths = 0
    for player in players.player_id:
        health = model.predict(model.load_data(game_date, player))
        write_db(health_update, health=health, player_id=player, game_date=game_date, connection=connection)
        healths += 1
    logger.info(f'Healths Predicted: {healths}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Model Database Calculations')
    parser.add_argument('-p', '--phealth', action='store_true')
    parser.add_argument('-w', '--win', action='store_true')
    parser.add_argument('-i', '--impact', action='store_true')
    parser.add_argument('--win_model', help='win model file path, required if calculating win probability or impact')
    parser.add_argument('--covid_model', help='health model file path, required if calculating health')
    parser.add_argument('-d', '--date', help='pass csv file path or date in format YYYY-MM-DD')
    parser.add_argument('-s', '--season', type=int, default=2022, help='seasons stats to use')
    args = parser.parse_args()
    kwargs = {}
    if args.date is None:
        kwargs['game_date'] = date.today()
    elif args.date.endswith('.csv'):
        dates = pd.read_csv(args.date, parse_dates=['game_date'])
        kwargs['game_date'] = dates.loc[0, 'game_date']
        dates.drop([0], axis=0, inplace=True)
    else:
        kwargs['game_date'] = datetime.strptime(args.date, '%Y-%m-%d')
    logger.info(f'Executing with Date: {kwargs["game_date"].strftime("%Y-%m-%d")}')

    if args.win or args.impact:
        try:
            assert args.win_model is not None
        except AssertionError:
            logger.error("A Win Probability Model must be specified")
            raise
        try:
            win_model = NBACoV(resolve_path(args.win_model))
            logger.info('Win Probability Model Loaded Successfully')
        except FileNotFoundError:
            logger.error(f"{args.win_model} does not exist nor exist in registry (/mnt/ml-nba/models)")
            raise
    if args.phealth:
        try:
            assert args.covid_model is not None
        except AssertionError:
            logger.error("A Health Model must be specified")
            raise
        try:
            health_model = NBACovid(resolve_path(args.covid_model))
            logger.info('Health Model Loaded Successfully')
        except FileNotFoundError:
            logger.error(f"{args.covid_model} does not exist nor exist in registry (/mnt/ml-nba/models)")
            raise
    kwargs['season'] = args.season
    logger.info(f"Using Season: {kwargs['season']}")
    try:
        with get_engine().begin() as conn:
            kwargs['connection'] = conn
            if args.phealth:
                calculate_health(model=health_model, **kwargs)
            health_score = NBACovid.score_model(end_date=kwargs['game_date'])
        with get_engine().begin() as conn:
            kwargs['connection'] = conn
            if args.win:
                calculate_win_prob(model=win_model, **kwargs)
            if args.impact:
                calculate_impact(model=win_model, **kwargs)
            win_score = NBACoV.score_model(end_date=kwargs['game_date'])
    except ConnectionError:
        logger.error('Database Connection Failed!')
    if health_score < .5:
        logger.warning(f'Health Model has Degraded!\n R2 score over the past week: {health_score}')
    if win_score < .65:
        logger.warning(f'Win Model has Degraded!\n Accuracy over the past week: {win_score}')
    if args.date is not None and args.date.endswith('.csv'):
        logger.info(f'Dates saved to {args.date}')
        dates.to_csv(args.date, index=False)

