import argparse
from sqlalchemy.engine import Connection
import pandas as pd
from datetime import date, timedelta, datetime
from modeling.chance_of_victory import NBACoV
from modeling.covid_recovery import NBACovid
from modeling import func_timer
from modeling.utils import read_table, get_engine, write_db

player_impact = 'select game_date, player_id, season, team, health, impact from nba.ACTIVE_ROSTER_DUMMY ' \
                'where GAME_DATE <= :game_date order by PLAYER_ID, GAME_DATE'
impact_update = 'update nba.active_roster_dummy set impact = :impact where GAME_DATE = :game_date and PLAYER_ID = :player_id'
health_calc = "SELECT player_id from ACTIVE_ROSTER_DUMMY where GAME_DATE = :today and HEALTH = -1"
health_update = "update active_roster_dummy set health = :health, PRED_HEALTH = :health where PLAYER_ID = :player_id and game_date = :game_date"
win_prob = "SELECT GAME_DATE, HOME FROM NBA.SCHEDULE WHERE GAME_DATE = :today"
win_update = "update schedule set HOME_WIN_PROB = :home_win, AWAY_WIN_PROB = :away_win where GAME_DATE = :game_date and HOME = :team"


@func_timer
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
    print(f'Impacts Calculated: {impact_generated}')


@func_timer
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
    print(f'Games Predicted:   {wins}')


@func_timer
def calculate_health(game_date, model, connection: Connection, *args, **kwargs):
    players = read_table(health_calc, today=game_date)
    healths = 0
    for player in players.player_id:
        health = model.predict(model.load_data(game_date, player))
        write_db(health_update, health=health, player_id=player, game_date=game_date, connection=connection)
        healths += 1
    print(f'Healths Predicted: {healths}')


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

    if args.win or args.impact:
        assert args.win_model is not None, "A Win Probability Model must be specified"
        win_model = NBACoV(args.win_model)
    if args.phealth:
        assert args.covid_model is not None, "A Health Model must be specified"
        health_model = NBACovid(args.covid_model)
    kwargs['season'] = args.season

    with get_engine().begin() as conn:
        kwargs['connection'] = conn
        if args.phealth:
            calculate_health(model=health_model, **kwargs)
    with get_engine().begin() as conn:
        kwargs['connection'] = conn
        if args.win:
            calculate_win_prob(model=win_model, **kwargs)
        if args.impact:
            calculate_impact(model=win_model, **kwargs)
    if args.date is not None and args.date.endswith('.csv'):
        dates.to_csv(args.date, index=False)

