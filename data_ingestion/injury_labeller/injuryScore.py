import os
from datetime import datetime
import numpy as np
from haversine import haversine
import pandas as pd
from data_ingestion import Dataset
from basketball_reference_scraper.players import get_game_logs
from basketball_reference_scraper.box_scores import get_box_scores
EARTH_RADIUS = 3958.8


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
        'SAC': 'Sacremento Kings',
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

    def __init__(self, name: str, year: int):
        self.injuries = Dataset._read_db(self.Data)
        self.cities = Dataset._read_db(self.Stadiums)
        self.cities.index = self.cities.pop('team')
        self.player = get_game_logs(name, year).fillna(0)
        self.name = name

    def __call__(self, name: str, year: int):
        self.player = get_game_logs(name, year).fillna(0)
        self.name = name
        return self

        
    @staticmethod
    def dist(lat1: float, long1: float, lat2: float, long2: float) -> float:
        """
        calculates distance based on mathematical latitude and longitudinal calculations
        https://towardsdatascience.com/realigning-sports-leagues-with-a-clustering-algorithm-d6e9de9294d0
        :param lat1: latitude of present city
        :param lat2: latitude of city being travelled to
        :param long1: longitude of present city
        :param long2: longitude of city being travelled to
        :return: mathematically calculated distance between points
        """
        
        lat1, lat2 = np.deg2rad(lat1), np.deg2rad(lat2)
        long1, long2 = np.deg2rad(long1), np.deg2rad(long2)

        return EARTH_RADIUS * np.arccos((np.sin(lat1) * np.sin(lat2)) + 
               np.cos(lat1) * np.cos(lat2) * np.cos(long2 - long1))

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
    def regressionCalc(injury: str) -> float:
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


    @staticmethod
    def getDayDiff(day1, day2):
        """
        calculates distance between days
        :param day1: initial day
        :param day2: final day
        :return: difference between days
        """
        x = datetime.strptime(day1, "%Y-%m-%d")
        y = datetime.strptime(day2, "%Y-%m-%d")
        return (x-y).days

    def playerToDf(self, name, year):
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

    def idToDf(self, id, year):
        """
        Translate BBallRefID to a pandas dataframe
        :param id: id of the player
        :param year: season year -> ex: represent 2016-2017 season as 2017
        :return: df for season played
        """
        name_to_ref = Dataset._read_csv(self.IDs)
        name_to_ref = name_to_ref.loc[name_to_ref['BBRefID'] == id]
        link = name_to_ref['BBRefLink'].values[0]
        link = link.replace('.html', '')
        link += '/gamelog/' + str(year)
        df = pd.read_html(link)[7]
        df.columns = ['Rk','G','Date','Age','Tm','Home','Opp','Blank','GS','MP','FG','FGA','FG%','3P','3PA','3P%','FT','FTA','FT%','ORB','DRB','TRB','AST','STL','BLK','TOV','PF','PTS','GmSc','+/-']
        df = df[df.Tm != 'Tm']
        return df


    def idToName(self, id):
        """
        translate BBallRef ID to the name of the player
        :param id: id of the player
        :return name: name of the player
        """
        name_to_ref = Dataset._read_csv(self.IDs)
        name_to_ref = name_to_ref.loc[name_to_ref['BBRefID'] == id]
        return name_to_ref.BBRefName.values[0]

    def distRegressor(self, dist):
        """
        calculates regressor based on distance travelled between games
        :param dist: distance travelled between games
        :return: regressor based on distance travelled
        """
        if dist == 0:
            distRegress = 0.10
        elif dist < 1000:
            distRegress = -0.10
        elif dist < 2000:
            distRegress = -0.15
        else: 
            distRegress = -0.20
        return distRegress

    def timeRegressor(self, days):
        """
        calculates regressor based on time between games
        :param days: time travelled between games
        :return: regressor based on time between games
        """
        days_bonus = {
            1: 0,
            2: .05,
            3: .10
        }
        return days_bonus.get(days, .15)

    def minsRegress(self, minutes):
        """
        calculates regressor based on minutes played in the past few games
        :param minutes: time played in the previous game
        :return: regressor based on minutes based on the previous game
        """
        mins = int(minutes) if minutes.isnumeric() else 0
        if mins < 20:
            mins_regressor = 0
        elif mins < 30:
            mins_regressor = -0.10
        elif mins < 40:
            mins_regressor = -0.15
        else:
            mins_regressor = -0.20
        return mins_regressor

    def genInitLoc(self):
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
        prev_loc = self.genInitLoc()

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
                distRegress = self.distRegressor(dist)
                daysBonus = self.timeRegressor(days)
                minsRegressor = self.minsRegress(row.MP[0:2])
                
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
        log.index = log.PLAYER
        log.loc[p, 'FG':] = log.loc[p, 'FG':].astype(float)
        log.loc[t, 'FG':] = log.loc[t, 'FG':].astype(float)
        return (log.loc[p, 'PTS'] + log.loc[p, 'FG'] + log.loc[p, 'FT'] - log.loc[p, 'FGA'] - log.loc[p, 'FTA'] +
                log.loc[p, 'DRB'] + log.loc[p, 'ORB'] / 2 + log.loc[p, 'AST'] + \
                log.loc[p, 'STL'] + log.loc[p, 'BLK'] / 2 - log.loc[p, 'PF'] - log.loc[p, 'TOV']) / (
                           log.loc[t, 'PTS'] + log.loc[t, 'FG'] + log.loc[t, 'FT'] - log.loc[p, 'FTA'] - \
                           log.loc[t, 'FGA'] + log.loc[t, 'DRB'] + log.loc[t, 'ORB'] / 2 + log.loc[t, 'AST'] + log.loc[
                               t, 'STL'] + log.loc[t, 'BLK'] / 2 - log.loc[t, 'PF'] - log.loc[t, 'TOV'])

    def pie_health_score(self):
        prev_date = self.player['DATE'].iloc[0]
        prev_loc = self.genInitLoc()
        query = "select pie from nba.player_stats where player = :player"
        base_pie = Dataset._read_db(query, player=self.name).iloc[0,0]
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
            injury = 0 if not result.empty else 1
            if row.MP[0:2] != 'In' and row.MP[0:2] != 'Di':  # Columns blocked off when player is out of the Game
                if i == 0:
                    health_value = 1
                else:
                    log = get_box_scores(row.DATE, row.TEAM, row.OPPONENT)[row.TEAM]
                    score = self.pie_score(log, self.name)
                    score = 0 if score < 0 else score
                    health_value = score/base_pie
                health_value = 1 if health_value > 1 else health_value
                health_value = .001 if health_value <= 0 else health_value
                row = [row.DATE, health_value, dist, days, int(row.MP[0:2]), injury]
                values.append(row)
            else:
                values.append([row.DATE, np.nan, dist, days, 0, injury])
        return pd.DataFrame(values, columns=['Date', 'Health', 'Distance', 'Days', 'MP', 'Injured'])

