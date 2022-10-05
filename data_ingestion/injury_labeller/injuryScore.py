import os
import numpy as np
from haversine import haversine
import pandas as pd
from data_ingestion.db_utils import read_table, timeout, write_db
from basketball_reference_scraper.players import get_game_logs
from basketball_reference_scraper.box_scores import get_box_scores
from collections import defaultdict


class InjuryScore:
    """
    Class for calculating the Injury Score for a player
    define inputs for creating and calculating injury score
    CSV - CSV of player inputted similar to BBall reference notation
    name - name of player, useful name from BBall reference
    """
    Data = "SELECT * FROM nba.active_roster where active = 0"  # Dataset.DataFile('covid_data/', 'NBA_Injury_Data.csv')
    Stadiums = "SELECT * FROM nba.stadiums where League = 'NBA'"  # Dataset.DataFile('injury_labeller/', 'stadiums.csv')
    IDs = "SELECT * FROM nba.player_ids"  # Dataset.DataFile('injury_labeller/', 'player_to_bballref.csv')
    teams_expanded = {
        'DAL': 'Dallas Mavericks',
        'ORL': 'Orlando Magic',
        'SAS': 'San Antonio Spurs',
        'DEN': 'Denver Nuggets',
        'BKN': 'Brooklyn Nets',
        'BRK': 'Brooklyn Nets',
        'UTA': 'Utah Jazz',
        'WAS': 'Washington Wizards',
        'GSW': 'Golden State Warriors',
        'LAC': 'Los Angeles Clippers',
        'LAL': 'Los Angeles Lakers',
        'MEM': 'Memphis Grizzlies',
        'MIL': 'Milwaukee Bucks',
        'PHX': 'Phoenix Suns',
        'PHO': 'Phoenix Suns',
        'MIA': 'Miami Heat',
        'IND': 'Indiana Pacers',
        'SAC': 'Sacramento Kings',
        'DET': 'Detroit Pistons',
        'PHI': 'Philadelphia 76ers',
        'NYK': 'New York Knicks',
        'POR': 'Portland Trail Blazers',
        'OKC': 'Oklahoma City Thunder',
        'CLE': 'Cleveland Cavaliers',
        'TOR': 'Toronto Raptors',
        'NOP': 'New Orleans Pelicans',
        'CHO': 'Charlotte Hornets',
        'ATL': 'Atlanta Hawks',
        'MIN': 'Minnesota Timberwolves',
        'BOS': 'Boston Celtics',
        'HOU': 'Houston Rockets',
        'CHI': 'Chicago Bulls',
    }
    days_bonus = defaultdict(
        lambda: .15,
        {
            1: 0,
            2: .05,
            3: .10,
        }
    )
    mins_reg = defaultdict(
        lambda: -.2,
        {
            0: 0,
            1: 0,
            2: -.1,
            3: -.15,
        }
    )
    dist_reg = defaultdict(
        lambda: -.2,
        {
            0: .1,
            1: -.1,
            2: -.15,
        }
    )

    def __init__(self, name: str, year: int):
        self.injuries = read_table(self.Data)
        self.cities = read_table(self.Stadiums)
        self.cities.index = self.cities.pop('team')
        self.player = get_game_logs(name, year).fillna(0)
        try:
            if ' ' in name:
                self.name = name
                self.player_id = read_table("select player_id from NBA.PLAYER_IDS where name = :name", name=name).iloc[0, 0]
            else:
                self.player_id = name
                self.name = read_table("select name from NBA.PLAYER_IDS where player_id = :name", name=name).iloc[0, 0]
        except IndexError as exc:
            raise ValueError("Player or ID cannot be found!") from exc

    def __call__(self, name: str, year: int):
        self.player = get_game_logs(name, year).fillna(0)
        try:
            if ' ' in name:
                self.name = name
                self.player_id = read_table("select player_id from NBA.PLAYER_IDS where name = :name", name=name).iloc[
                    0, 0]
            else:
                self.player_id = name
                self.name = read_table("select name from NBA.PLAYER_IDS where player_id = :name", name=name).iloc[0, 0]
        except IndexError as exc:
            raise ValueError("Player or ID cannot be found!") from exc
        return self

    def calc_dist(self, start, end):
        """
        calculates distance between two points with the Haversine Formula
        For reference, https://en.wikipedia.org/wiki/Haversine_formula
        :param self: class variables
        :param start: starting city 3 letter code
        :param end: destination city 3 letter code
        :return: haversine calculation in miles for the distance between two city
        """
        start = tuple(self.cities.loc[self.teams_expanded[start], 'lat':'LONG'])
        end = tuple(self.cities.loc[self.teams_expanded[end], 'lat':'LONG'])
        return haversine(start, end, unit='mi')

    @staticmethod
    def regression_calc(injury: str) -> float:
        """
        calculates injury regression value based on labels
        :param injury: string with injury designation
        :return: injury regression value
        """
        curr_inj = 'standard'
        inj_regress = -0.1
        if '(out for season)' in injury:
            curr_inj = 'EOS'
            inj_regress = -1
        elif 'sore' in injury:
            curr_inj = 'soreness'
            inj_regress = -0.10
        elif 'surgery' in injury:
            curr_inj = 'surgery recovery'
            inj_regress = -0.10
        elif 'injury' in injury:
            curr_inj = 'standard injury'
            inj_regress = -0.10

        return inj_regress

    def player_to_df(self, name, year):
        """
        returns csv for a player across a NBA season
        :param name: name of the player
        :param year: season year -> ex: represent 2016-2017 season as 2017
        :return: df for season played
        """
        name_to_ref = pd.read_csv(os.environ.get('MLNBA_ROOT', '~/work/ml-covid-nba') +
                                  "/ml-covid-nba/data/injury_labeller/player_to_bballref.csv")
        name_to_ref = name_to_ref.loc[name_to_ref['BBRefName'] == name]
        link = name_to_ref['BBRefLink'].values[0]
        link = link.replace('.html', '')
        link += '/gamelog/' + str(year)
        df = pd.read_html(link)[7]
        df.columns = ['Rk','G','Date','Age','Tm','Home','Opp','Blank','GS','MP','FG','FGA','FG%','3P','3PA','3P%','FT','FTA','FT%','ORB','DRB','TRB','AST','STL','BLK','TOV','PF','PTS','GmSc','+/-']
        df = df[df.Tm != 'Tm']
        return df

    def id_to_df(self, id_, year):
        """
        Translate BBallRefID to a pandas dataframe
        :param id_: id of the player
        :param year: season year -> ex: represent 2016-2017 season as 2017
        :return: df for season played
        """
        query = "select name from nba.player_ids where player_id = :player"
        name_to_ref = read_table(query, player=id_).iloc[0,0]
        df = get_game_logs(name_to_ref, year)
        return df

    def id_to_name(self, id_):
        """
        translate BBallRef ID to the name of the player
        :param id_: id of the player
        :return name: name of the player
        """
        name_to_ref = read_table(self.IDs)
        name_to_ref = name_to_ref.loc[name_to_ref['BBRefID'] == id_]
        return name_to_ref.BBRefName.values[0]

    def dist_regressor(self, dist):
        """
        calculates regressor based on distance travelled between games
        :param dist: distance travelled between games
        :return: regressor based on distance travelled
        """
        return self.dist_reg[int(dist / 1000) + 1 if dist != 0 else 0]

    def time_regressor(self, days):
        """
        calculates regressor based on time between games
        :param days: time travelled between games
        :return: regressor based on time between games
        """
        return self.days_bonus[days]

    def mins_regress(self, minutes):
        """
        calculates regressor based on minutes played in the past few games
        :param minutes: time played in the previous game
        :return: regressor based on minutes based on the previous game
        """
        mins = int(minutes) if minutes.isnumeric() else 0
        return self.mins_reg[int(mins/10)]

    def init_loc(self):
        """
        calculates initial location of the first game of the season
        :param self: class variable
        :return: 3 letter code for location of the first game of the season
        """
        if self.player['HOME/AWAY'].iloc[0] == 'HOME':
            prev_loc = self.player['TEAM'].iloc[0]
        else: 
            prev_loc = self.player['OPPONENT'].iloc[0]
        return prev_loc

    def getInjuryScore(self):
        """
        calculate injury score based on weights and flat injury for a given season
        :param self: class variable
        :return: DF with extra column for Injury and Fatigue Score for the player
        """
        # get date and location for the first game of the season
        prev_date = self.player['DATE'].iloc[0]
        prev_loc = self.init_loc()

        cnt = 0  # counter for debugging
        values = [1]  # use list to store Injury and Fatigue Score

        for _, row in self.player.iterrows():
            if row.MP[0:2] != 'In' and row.MP[0:2] != 'Di':  # Columns blocked off when player is out of the Game
                # 0.6 denotes out of game, but we start player
                # off at 0.8 one return to account for rest and lack of game speed
                if values[-1] == 0.6:
                    values[-1] = 0.8
                # get distance between previous game and next game(initial
                # game counts as 0 travel distance) and set location for the next game
                if row['HOME/AWAY'] == 'AWAY':
                    dist = self.calc_dist(prev_loc, row.OPPONENT)
                    prev_loc = row.OPPONENT
                else:
                    dist = self.calc_dist(prev_loc, row.TEAM)
                    prev_loc = row.TEAM

                # calculate difference in days between days
                days = (row.DATE - prev_date).days
                prev_date = row.DATE

                # calculate injury regressor from injury database
                result = self.injuries[(self.injuries['player'] == self.name) & (self.injuries['game_date'] == row.DATE)]
                if not result.empty:
                    injury = -.1  # self.regressionCalc(result.Notes)
                else: 
                    injury = 0

                # calculate distance regressor, time regressor, and minutes regressor
                distRegress = self.dist_regressor(dist)
                daysBonus = self.time_regressor(days)
                minsRegressor = self.mins_regress(row.MP[0:2])
                
                # use predetermined weights to calculate health value
                healthValue = values[-1] + (0.33 * distRegress) + (0.33 * minsRegressor) + (0.33 * daysBonus) + injury
                # cap value at 1
                if healthValue >= float(1):
                    values.append(1.0)
                else:
                    values.append(healthValue)
                cnt += 1
            else:
                values.append(0.6)
        # remove initial value, add to DF and return important columns
        self.player['Injury and Fatigue Score'] = values[1:]
        return self.player[['DATE', 'Injury and Fatigue Score', 'MP']]

    @staticmethod
    def pie_score(log, p):
        t = 'Team Totals'
        log.index = log.player_id
        log.index.values[-1] = t
        log.loc[p, 'FG':'+/-'] = log.loc[p, 'FG':'+/-'].astype(float)
        log.loc[t, 'FG':'+/-'] = log.loc[t, 'FG':'+/-'].astype(float)
        return (log.loc[p, 'PTS'] + log.loc[p, 'FG'] + log.loc[p, 'FT'] - log.loc[p, 'FGA'] - log.loc[p, 'FTA'] +
                log.loc[p, 'DRB'] + log.loc[p, 'ORB'] / 2 + log.loc[p, 'AST'] + \
                log.loc[p, 'STL'] + log.loc[p, 'BLK'] / 2 - log.loc[p, 'PF'] - log.loc[p, 'TOV']) / (
                           log.loc[t, 'PTS'] + log.loc[t, 'FG'] + log.loc[t, 'FT'] - log.loc[p, 'FTA'] - \
                           log.loc[t, 'FGA'] + log.loc[t, 'DRB'] + log.loc[t, 'ORB'] / 2 + log.loc[t, 'AST'] + log.loc[
                               t, 'STL'] + log.loc[t, 'BLK'] / 2 - log.loc[t, 'PF'] - log.loc[t, 'TOV'])

    def pie_health_score(self):
        prev_date = self.player['DATE'].iloc[0]
        prev_loc = self.init_loc()
        query = "select pie from nba.player_stats where player_id = :player"
        base_pie = read_table(query, player=self.player_id).iloc[0,0]
        values = []  # use list to store Injury and Fatigue Score

        for i, row in self.player.iterrows():
            if row['HOME/AWAY'] == 'AWAY':
                dist = self.calc_dist(prev_loc, row.OPPONENT)
                prev_loc = row.OPPONENT
            else:
                dist = self.calc_dist(prev_loc, row.TEAM)
                prev_loc = row.TEAM
            # calculate difference in days between days
            days = (row.DATE - prev_date).days
            prev_date = row.DATE

            # calculate injury regressor from injury database
            result = self.injuries[
                (self.injuries['player'] == self.name) & (self.injuries['game_date'] == row.DATE)]
            injury = 1 if not result.empty else 0
            covid = result.covid.values[0] if not result.empty else 0
            if row.MP[0:2] != 'In' and row.MP[0:2] != 'Di':  # Columns blocked off when player is out of the Game
                if i == 0:
                    health_value = 1
                else:
                    log = timeout(10, get_box_scores, func_args=(row.DATE, row.TEAM, row.OPPONENT))[row.TEAM]
                    score = self.pie_score(log, self.player_id)
                    score = 0 if score < 0 else score
                    health_value = score/base_pie
                health_value = 1 if health_value > 1 else health_value
                health_value = .001 if health_value <= 0 else health_value
                row = [row.DATE, health_value, dist, days, int(row.MP.split(':')[0]), injury, covid]
                values.append(row)
            else:
                values.append([row.DATE, np.nan, dist, days, 0, injury, covid])
        return pd.DataFrame(values, columns=['Date', 'Health', 'Distance', 'Days', 'MP', 'Injured', 'Covid'])



