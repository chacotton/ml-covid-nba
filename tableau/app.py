import os
from datetime import date, timedelta, datetime
from itertools import product
from flask import Flask, render_template, request, redirect, url_for, _app_ctx_stack
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from utils import read_table, WinProbWrapper, SessionLocal, get_odds
import pickle
from constants import team_colors, layouts
from collections import namedtuple
from sqlalchemy.orm import scoped_session
import greenlet
import schedule
from copy import deepcopy


app = Flask(__name__)
app.session = scoped_session(SessionLocal, scopefunc=greenlet.getcurrent)
with open('game_opts.pkl', 'rb') as f:
    app.game_opts = pickle.load(f)
    app.game_opts['2020-21'] = app.game_opts.pop('2021')
    app.game_opts['2021-22'] = app.game_opts.pop('2022')
    app.game_opts['2022-23'] = app.game_opts.pop('2023')
app.model = WinProbWrapper(os.getenv('MODEL_PATH', '') + 'classifier_v2/artifacts/xgb_classifier.json', app.session)
app.today = date(1970, 1, 1)
app.curr_game_opts = {}
app.spreads = {}

HOME = "select home, away, HOME_PTS, AWAY_PTS, HOME_WIN_PROB, AWAY_WIN_PROB from SCHEDULE where GAME_DATE = :game_date"
COVID = "select player, abs(sum(impact)) from NBA.ACTIVE_ROSTER_DUMMY where COVID = 1 and SEASON = 2023 group by PLAYER having sum(impact) < 0 order by 2 fetch next 5 rows only"
Game = namedtuple("Game", "season game_date team")
curr_game = None
curr_players = {}

def manage_game_opts(today):
    app.curr_game_opts = deepcopy(app.game_opts)
    for k in app.game_opts['2022-23'].keys():
        year = 2022 if int(k[:2]) > 7 else 2023
        if date(year, int(k[:2]), int(k[-2:])) > today:
            app.curr_game_opts['2022-23'].pop(k)

def manage_today():
    app.today = date.today()

def manage_spreads():
    app.spreads = get_odds()


manage_today()
manage_game_opts(app.today)
manage_spreads()

schedule.every().day.at("10:00").do(manage_today)
schedule.every().day.at("10:01").do(manage_game_opts, today=app.today)
schedule.every().day.at("10:00").do(manage_spreads)


def search():
    season = request.form.get('season')
    return season

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    yday = read_table(HOME, game_date=app.today - timedelta(days=1), connection=app.session)
    tday = read_table(HOME, game_date=app.today, connection=app.session)
    yday_tables = ''
    for i, row in yday.iterrows():
        df = pd.DataFrame([[row.away, row.away_pts, f'{row.away_win_prob*100:.1f}%'],
                           [row.home, row.home_pts, f'{row.home_win_prob*100:.1f}%']],
                          columns=['Team', 'Score', 'W%']).to_html(border=1, index=False,
                                                                   col_space=[150,50,50],
                                                                   justify='center')
        df = df.replace('dataframe','box_score')
        yday_tables += (df + "<br>")
    rows, cols, h = layouts.get(len(tday), (5, 3, 650))
    specs = [[{"type": "pie"} for _ in range(cols)] for _ in range(rows)]
    fig = make_subplots(rows=rows, cols=cols, specs=specs)
    locs = list(product(list(range(1, rows + 1)), list(range(1, cols + 1))))
    s = pd.Series(team_colors)
    for i, row in tday.iterrows():
        row_l, col = locs.pop(0)
        fig.add_trace(go.Pie(labels=[row.home, row.away], values=[row.home_win_prob, row.away_win_prob],
                             text=[row.home, row.away],
                             textposition='outside', marker={'colors': s[[row.home, row.away]]},
                             hovertemplate='%{label}: %{percent}<extra></extra>'),
                      row=row_l, col=col)
    title = f'Games on {app.today.strftime("%m/%d")}'
    if len(tday) < 1:
        title += '<br>No Games Today'
    fig.update_layout(showlegend=False, title_text=title, title_x=.5, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=h,
                      xaxis={'showgrid': False, 'zeroline': False, 'visible': False}, yaxis={'showgrid': False, 'zeroline': False, 'visible': False})
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    df = read_table(COVID, connection=app.session)
    df.columns = ['Player', 'Losses']
    fig = px.bar(data_frame=df, y='Player', x='Losses', orientation='h', height=300)
    fig.update_traces(hovertemplate="%{y}: %{x:.2f}")
    fig.update_layout(title_text="Most Impactful COVID-19 Illnesses - 2022-23",
                      title_x=.5, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': 'black'})
    mainGraph = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("home.html", yday_games=yday_tables, graphJSON=graphJSON,
                           scores_header=f"Scores - {(app.today - timedelta(days=1)).strftime('%m/%d')}",
                           mainGraph=mainGraph)

@app.route('/insights')
def insights():
    return render_template('insights.html')

@app.route('/game_plan', methods=['GET', 'POST'])
def game_plan():
    global curr_game
    global curr_players
    new_run = True
    if request.method == 'POST' and request.form.get('key', False) == 'select':
        season = request.form.get('season')
        game_date = request.form.get('date')
        team = request.form.get('team')
    elif request.method == 'POST' and request.form.get('key', False) == 'calc' and curr_game is not None:
        new_run = False
        season = curr_game.season
        game_date = curr_game.game_date
        team = curr_game.team
        curr_players[0] = [x if request.form.get(x, 0) != 0 else 0 for x in curr_players[0]]
        curr_players[1] = [x if request.form.get(x, 0) != 0 else 0 for x in curr_players[1]]
    else:
        season = '2022-23'
        game_date = list(app.curr_game_opts['2022-23'].keys())[-1]
        team = app.curr_game_opts['2022-23'][game_date][0]
    curr_game = Game(season, game_date, team)
    month, day = [int(x) for x in game_date.split('/')]
    if month > 7:
        season = f'20{season[2:4]}'
    else:
        season = f'20{season[-2:]}'

    game_date = date(int(season), month, day)

    game = read_table("select home, away, home_pts, away_pts, HOME_WIN_PROB, AWAY_WIN_PROB from NBA.SCHEDULE where GAME_DATE = :game_date and (HOME = :team or AWAY = :team)",
                          game_date=game_date, team=team, connection=app.session)
    home = read_table(
            "select player, active, PLAYER_ID from nba.ACTIVE_ROSTER_DUMMY where GAME_DATE = :game_date and TEAM = :team",
            game_date=game_date, team=game.loc[0, 'home'], connection=app.session)
    away = read_table(
            "select player, active, PLAYER_ID from nba.ACTIVE_ROSTER_DUMMY where GAME_DATE = :game_date and TEAM = :team",
            game_date=game_date, team=game.loc[0, 'away'], connection=app.session)
    if new_run:
        home_actives = home[home.active == 1].player_id.tolist()
        away_actives = away[away.active == 1].player_id.tolist()
    else:
        home_actives = [x for x in curr_players[0] if x != 0]
        away_actives = [x for x in curr_players[1] if x != 0]
    pred = app.model.predict(home_actives, away_actives, season=season, game_date=game_date, home=game.loc[0, 'home'])
    fig = px.pie(names=game.loc[0, 'home':'away'],
                 values=pred,
                 color=game.loc[0, 'home':'away'],
                 color_discrete_map=team_colors,
                 )
    fig.update_traces(hovertemplate='%{label}: %{percent}<extra></extra>')
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
    away_score = game.loc[0, 'away_pts'] if game.loc[0, 'away_pts'] > 0 else app.spreads.get(game.loc[0, 'away'], '')
    home_score = game.loc[0, 'home_pts'] if game.loc[0, 'home_pts'] > 0 else app.spreads.get(game.loc[0, 'home'], '')
    return render_template('game_plan.html', away=game.loc[0,'away'], home=game.loc[0,'home'],
                           away_score=away_score, home_score=home_score,
                           graphJSON=graphJSON, away_roster=away, home_roster=home,
                           game_opts=app.curr_game_opts, home_logo=game.loc[0, 'home'].lower().replace(' ',"_"),
                           away_logo=game.loc[0, 'away'].lower().replace(' ', '_'))

