from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import plotly
import plotly.express as px
import json
from utils import read_table, get_engine
from datetime import date
import pickle
from constants import team_colors

app = Flask(__name__)
with open('game_opts.pkl', 'rb') as f:
    app.game_opts = pickle.load(f)



def get_game_opts():
    seasons = read_table('select distinct season from NBA.SCHEDULE')
    game_opts = {str(k): {} for k in seasons.season.values}
    for season in game_opts:
        game_dates = read_table('select distinct game_date from NBA.SCHEDULE where SEASON = :season', season=int(season))
        for game_date in game_dates.game_date:
            teams = read_table('select away,home from nba.SCHEDULE where GAME_DATE = :game_date', game_date=game_date)
            teams = teams.away.tolist() + teams.home.tolist()
            game_opts[season][game_date.strftime('%m/%d')] = teams
    return game_opts


def search():
    season = request.form.get('season')
    return season

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return redirect(url_for('insights'))

@app.route('/insights')
def insights():
    return render_template('insights.html')

@app.route('/game_plan', methods=['GET', 'POST'])
def game_plan():
    season = int(request.form.get('season', 2023))
    game_date = request.form.get('date', '10/26')
    team = request.form.get('team', 'Detroit Pistons')
    month, day = [int(x) for x in game_date.split('/')]
    if month > 7:
        season -= 1
    game_date = date(season, month, day)
    with get_engine().connect() as conn:
        game = read_table("select home, away, home_pts, away_pts, HOME_WIN_PROB, AWAY_WIN_PROB from NBA.SCHEDULE where GAME_DATE = :game_date and (HOME = :team or AWAY = :team)",
                          game_date=game_date, team=team, connection=conn)
        home = read_table(
            "select player, active from nba.ACTIVE_ROSTER_DUMMY where GAME_DATE = :game_date and TEAM = :team",
            game_date=game_date, team=game.loc[0, 'home'], connection=conn)
        away = read_table(
            "select player, active from nba.ACTIVE_ROSTER_DUMMY where GAME_DATE = :game_date and TEAM = :team",
            game_date=game_date, team=game.loc[0, 'away'], connection=conn)
    fig = px.pie(names=game.loc[0,'home':'away'],
                 values=game.loc[0,'home_win_prob':'away_win_prob'],
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
    exp = {0: '@', 1: '?'}
    for i, data in enumerate(dfs):
        data.replace({'active': exp}, inplace=True)
        data.columns = ['Players', 'Active']
        data = data.to_html(border=0, index=False, col_space=50, justify='center')
        data = data.replace('?', '<input type="checkbox" checked>')
        data = data.replace('@', '<input type="checkbox" >')
        dfs[i] = data
    home, away = dfs
    return render_template('game_plan.html', away=game.loc[0,'away'], home=game.loc[0,'home'],
                           away_score=game.loc[0,'away_pts'], home_score=game.loc[0,'home_pts'],
                           graphJSON=graphJSON, away_roster=away, home_roster=home,
                           game_opts=app.game_opts)

