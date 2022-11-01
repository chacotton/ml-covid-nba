from datetime import date, timedelta, datetime
from itertools import product
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from utils import read_table, get_engine, WinProbWrapper
import pickle
from constants import team_colors, layouts
from collections import namedtuple


app = Flask(__name__)
with open('game_opts.pkl', 'rb') as f:
    app.game_opts = pickle.load(f)
app.model = WinProbWrapper('/Users/chasecotton/ml-covid-nba/mlflow_utils/classifier_v2/artifacts/xgb_classifier.json')

HOME = "select home, away, HOME_PTS, AWAY_PTS, HOME_WIN_PROB, AWAY_WIN_PROB from SCHEDULE where GAME_DATE = :game_date"
Game = namedtuple("Game", "season game_date team")
curr_game = None
curr_players = {}

def manage_game_opts(today):
    bad_keys = []
    for k in app.game_opts['2023'].keys():
        if int(k[:2]) > 7:
            year = 2022
        else:
            year = 2023
        if date(year, int(k[:2]), int(k[-2:])) > today:
            bad_keys.append(k)
    for k in bad_keys:
        app.game_opts['2023'].pop(k)


def search():
    season = request.form.get('season')
    return season

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    today = date.today() if datetime.now().hour > 10 else date.today() - timedelta(days=1)
    with get_engine().connect() as conn:
        yday = read_table(HOME, game_date=today - timedelta(days=1), connection=conn)
        tday = read_table(HOME, game_date=today, connection=conn)
    yday_tables = ''
    for i, row in yday.iterrows():
        df = pd.DataFrame([[row.away, row.away_pts, f'{row.away_win_prob*100:.1f}%'],
                           [row.home, row.home_pts, f'{row.home_win_prob*100:.1f}%']],
                          columns=['Team', 'Score', 'W%']).to_html(border=1, index=False,
                                                                   col_space=[150,50,50],
                                                                   justify='center')
        df = df.replace('dataframe','box_score')
        yday_tables += (df + "<br>")
    rows, cols = layouts.get(len(tday), (5, 3))
    specs = [[{"type": "pie"} for i in range(cols)] for j in range(rows)]
    fig = make_subplots(rows=rows, cols=cols, specs=specs)
    locs = list(product(list(range(1, rows + 1)), list(range(1, cols + 1))))
    s = pd.Series(team_colors)
    for i, row in tday.iterrows():
        row_l, col = locs.pop(0)
        fig.add_trace(go.Pie(labels=[row.home, row.away], values=[row.home_win_prob, row.away_win_prob],
                             text=[row.home, row.away],
                             textposition='outside', marker={'colors': s[[row.home, row.away]]}),
                      row=row_l, col=col)
    fig.update_layout(showlegend=False, title_text='Games Today', title_x=.5, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("home.html", yday_games=yday_tables, graphJSON=graphJSON)

@app.route('/insights')
def insights():
    return render_template('insights.html')

@app.route('/game_plan', methods=['GET', 'POST'])
def game_plan():
    today = date.today() if datetime.now().hour > 10 else date.today() - timedelta(days=1)
    manage_game_opts(today)
    global curr_game
    global curr_players
    new_run = True
    if request.method == 'POST' and request.form.get('key', False) == 'select':
        season = int(request.form.get('season'))
        game_date = request.form.get('date')
        team = request.form.get('team')
    elif request.method == 'POST' and request.form.get('key', False) == 'calc' and curr_game is not None:
        new_run = False
        season = curr_game.season
        game_date = curr_game.game_date
        team = curr_game.team
        curr_players[0] = [x if request.form.get(x, 0) != 0 else 0 for x in curr_players[0]]
        curr_players[1] = [x if request.form.get(x, 0) != 0 else 0 for x in curr_players[1]]
        print(curr_players)
    else:
        season = 2023
        game_date = '10/26'
        team = 'Detroit Pistons'
    curr_game = Game(season, game_date, team)
    month, day = [int(x) for x in game_date.split('/')]
    if month > 7:
        season -= 1
    game_date = date(season, month, day)
    with get_engine().connect() as conn:
        game = read_table("select home, away, home_pts, away_pts, HOME_WIN_PROB, AWAY_WIN_PROB from NBA.SCHEDULE where GAME_DATE = :game_date and (HOME = :team or AWAY = :team)",
                          game_date=game_date, team=team, connection=conn)
        home = read_table(
            "select player, active, PLAYER_ID from nba.ACTIVE_ROSTER_DUMMY where GAME_DATE = :game_date and TEAM = :team",
            game_date=game_date, team=game.loc[0, 'home'], connection=conn)
        away = read_table(
            "select player, active, PLAYER_ID from nba.ACTIVE_ROSTER_DUMMY where GAME_DATE = :game_date and TEAM = :team",
            game_date=game_date, team=game.loc[0, 'away'], connection=conn)
    if new_run:
        home_actives = home[home.active == 1].player_id.tolist()
        away_actives = away[away.active == 1].player_id.tolist()
    else:
        home_actives = [x for x in curr_players[0] if x != 0]
        away_actives = [x for x in curr_players[1] if x != 0]
    pred = app.model.predict(home_actives, away_actives, season=season, game_date=game_date, home=game.loc[0, 'home'], away=game.loc[0, 'away'])
    fig = px.pie(names=game.loc[0, 'home':'away'],
                 values=pred,
                 color=game.loc[0, 'home':'away'],
                 color_discrete_map=team_colors)
    fig.update_layout(legend={
        'orientation': 'h',
        'x': .5,
        'xanchor': 'center',
        'y': -.1
    })
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    dfs = [home, away]
    for i, data in enumerate(dfs):
        data.columns = ['Players', 'Active', 'pid']
        data.sort_values(by='Players', inplace=True)
        if not new_run:
            data.Active = curr_players[i]
        curr_players[i] = data.pid.tolist()
        data.Active = data.apply(lambda r: f'<input type="checkbox" name="{r.pid}" {"checked" if r.Active else ""}>', axis=1)
        data = data.to_html(border=0, index=False, col_space=50, justify='center', columns=['Players', 'Active'])
        data = data.replace('&lt;', '<').replace('&gt;', '>')
        dfs[i] = data
    home, away = dfs
    away_score = game.loc[0, 'away_pts'] if game.loc[0, 'away_pts'] > 0 else ''
    home_score = game.loc[0, 'home_pts'] if game.loc[0, 'home_pts'] > 0 else ''
    return render_template('game_plan.html', away=game.loc[0,'away'], home=game.loc[0,'home'],
                           away_score=away_score, home_score=home_score,
                           graphJSON=graphJSON, away_roster=away, home_roster=home,
                           game_opts=app.game_opts, home_logo=game.loc[0, 'home'].lower().replace(' ',"_"),
                           away_logo=game.loc[0, 'away'].lower().replace(' ', '_'))

