from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score
from urllib.request import urlopen
from bs4 import BeautifulSoup
from haversine import haversine
import pprint
import pandas as pd
from sklearn.model_selection import train_test_split
from matplotlib import pyplot
from data import Dataset
pd.set_option('display.max_rows', None)

class injuryScore:
    """
    Class for calculating the Injury Score for a player
    define inputs for creating and calculating injury score
    CSV - CSV of player inputted similar to BBall reference notation
    name - name of player, use full name from BBall reference
    """
    Data = Dataset.DataFile('covid_data/', 'NBA_Injury_Data.csv')
    Stadiums = Dataset.DataFile('injury_labeller/', 'stadiums.csv')
    IDs = Dataset.DataFile('injury_labeller/', 'player_to_bballref.csv')

    def __init__(self, id, year):
        self.injuries = Dataset._read_csv(self.Data)
        df_cities = Dataset._read_csv(self.Stadiums)
        self.cities = df_cities[df_cities['League'] == 'NBA']
        self.player = self.idToDf(id, year)
        self.name = self.idToName(id)
        self.teams_expanded = {'DAL': 'Dallas Mavericks', 
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
        
    '''
    calculates distance based on mathematical latitude and longitudinal calculations
    https://towardsdatascience.com/realigning-sports-leagues-with-a-clustering-algorithm-d6e9de9294d0
    :param lat1: latitude of present city
    :param lat2: latitude of city being travelled to
    :param long1: longitude of present city
    :param long2: longitude of city being travelled to
    :return: mathematically calculated distance between points
    '''
    def dist(lat1, long1, lat2, long2):
        
        lat1, lat2 = np.deg2rad(lat1), np.deg2rad(lat2)
        long1, long2 = np.deg2rad(long1), np.deg2rad(long2)
        EARTH_RADIUS = 3958.8
        return EARTH_RADIUS * np.arccos((np.sin(lat1) * np.sin(lat2)) + 
                            np.cos(lat1) * np.cos(lat2) * np.cos(long2 - long1))
    '''
    calculates distance between two points with the Haversine Formula
    For reference, https://en.wikipedia.org/wiki/Haversine_formula
    :param self: class variables
    :param start: starting city 3 letter code
    :param end: destination city 3 letter code
    :return: haversine calculation in miles for the distance between two city
    '''
    def calcDist(self, start, end):
        start_long = self.cities.loc[self.cities.Team == self.teams_expanded[start], 'Long'].tolist()[0]
        start_lat = self.cities.loc[self.cities.Team == self.teams_expanded[start], 'Lat'].tolist()[0]
        end_long = self.cities.loc[self.cities.Team == self.teams_expanded[end], 'Long'].tolist()[0]
        end_lat = self.cities.loc[self.cities.Team == self.teams_expanded[end], 'Lat'].tolist()[0]
        return haversine((start_lat, start_long),(end_lat, end_long), unit='mi')
    
    '''
    calculates injury regression value based on labels
    :param self: string with injury designation
    :return: injury regression value
    '''
    def regressionCalc(injury):
        currInj = 'standard'
        injRegress = -0.10
        if '(out for season)' in injury:
            currInj = 'EOS'
            injRegress = -1
        elif 'sore' in injury:
            currInj = 'soreness' 
            injRegress = -0.10
        elif 'surgery' in injury:
            currInj = 'surgery recovery' 
            injRegress = -0.10
        elif 'injury' in injury:
            currInj = 'standard injury'
            injRegress = -0.10

        return injRegress

    '''
    calculates distance between days
    :param day1: initial day
    :param day2: final day
    :return: difference between days
    '''
    def getDayDiff(day1, day2): 
        x = datetime.strptime(day1, "%Y-%m-%d")
        y = datetime.strptime(day2, "%Y-%m-%d")
        return (x-y).days
    '''
    returns csv for a player across a NBA season
    :param name: name of the player
    :param year: season year -> ex: represent 2016-2017 season as 2017
    :return: df for season played
    '''
    def playerToDf(self, name, year):
        name_to_ref = pd.read_csv("player_to_bballref.csv")
        name_to_ref = name_to_ref.loc[name_to_ref['BBRefName'] == name]
        link = name_to_ref['BBRefLink'].values[0]
        link = link.replace('.html', '')
        link += '/gamelog/' + str(year)
        df = pd.read_html(link)[7]
        df.columns = ['Rk','G','Date','Age','Tm','Home','Opp','Blank','GS','MP','FG','FGA','FG%','3P','3PA','3P%','FT','FTA','FT%','ORB','DRB','TRB','AST','STL','BLK','TOV','PF','PTS','GmSc','+/-']
        df = df[df.Tm != 'Tm']
        return df
    '''
    Translate BBallRefID to a pandas dataframe
    :param id: id of the player
    :param year: season year -> ex: represent 2016-2017 season as 2017
    :return: df for season played
    '''
    def idToDf(self, id, year):
        name_to_ref = Dataset._read_csv(self.IDs)
        name_to_ref = name_to_ref.loc[name_to_ref['BBRefID'] == id]
        link = name_to_ref['BBRefLink'].values[0]
        link = link.replace('.html', '')
        link += '/gamelog/' + str(year)
        df = pd.read_html(link)[7]
        df.columns = ['Rk','G','Date','Age','Tm','Home','Opp','Blank','GS','MP','FG','FGA','FG%','3P','3PA','3P%','FT','FTA','FT%','ORB','DRB','TRB','AST','STL','BLK','TOV','PF','PTS','GmSc','+/-']
        df = df[df.Tm != 'Tm']
        return df
    '''
    translate BBallRef ID to the name of the player
    :param id: id of the player
    :return name: name of the player
    '''
    def idToName(self, id):
        name_to_ref = Dataset._read_csv(self.IDs)
        name_to_ref = name_to_ref.loc[name_to_ref['BBRefID'] == id]
        return name_to_ref.BBRefName.values[0]
    '''
    calculates regressor based on distance travelled between games
    :param dist: distance travelled between games
    :return: regressor based on distance travelled
    '''
    def distRegressor(dist):
        if dist == 0:
            distRegress = 0.10
        elif dist < 1000:
            distRegress = -0.10
        elif dist < 2000:
            distRegress = -0.15
        else: 
            distRegress = -0.20
        return distRegress
    '''
    calculates regressor based on time between games
    :param days: time travelled between games
    :return: regressor based on time between games
    '''
    def timeRegressor(days):
        if days == 1:
            daysBonus = 0
        elif days == 2:
            daysBonus = 0.05
        elif days == 3: 
            daysBonus = 0.10
        else:
            daysBonus = 0.15
        return daysBonus
    '''
    calculates regressor based on minutes played in the past few games
    :param minutes: time played in the previous game
    :return: regressor based on minutes based on the previous game
    '''
    def minsRegress(minutes):
        if re.search('[a-zA-Z]', minutes) == False:
            if int(minutes) < 20:
                minsRegressor = 0
            elif int(minutes) < 30:
                minsRegressor = -0.10
            elif int(minutes) < 40:
                minsRegressor = -0.15
            else: 
                minsRegressor = -0.20
        else:
            minsRegressor = 0
        return minsRegressor
    '''
    calculates initial location of the first game of the season
    :param self: class variable
    :return: 3 letter code for location of the first game of the season
    '''
    def genInitLoc(self):
        prevLoc = ''
        if self.player['Date'].iloc[0] == None:
            prevLoc = self.player['Home'].iloc[0]
        else: 
            prevLoc = self.player['Opp'].iloc[0]
        return prevLoc
    '''
    calculate injury score based on weights and flat injury for a given season
    :param self: class variable
    :return: DF with extra column for Injury and Fatigue Score for the player
    '''
    def getInjuryScore(self):
        #get date and location for the first game of the season
        prevDate = self.player['Date'].iloc[0]  
        prevLoc = injuryScore.genInitLoc(self)

        cnt = 0 #counter for debugging
        values = [1] #use list to store Injury and Fatigue Score

        for row in self.player.itertuples():
            if row.MP[0:2] != 'In' and row.MP[0:2] != 'Di':  #Columns blocked off when player is out of the Game
                #0.6 denotes out of game but we start player off at 0.8 one return to account for rest and lack of game speed
                if values[-1] == 0.6:
                    values[-1] = 0.8
                #get distance between previous game and next game(initial game counts as 0 travel distance) and set location for the next game
                if row.Home == '@':
                    dist = injuryScore.calcDist(self, prevLoc, row.Opp)
                    prevLoc = row.Opp
                else:
                    dist = injuryScore.calcDist(self, prevLoc, row.Tm)
                    prevLoc = row.Tm

                #calculate difference in days between days
                days = injuryScore.getDayDiff(row.Date, prevDate)
                #reset date
                prevDate = row.Date

                #calculate injury regressor from injury database
                result = self.injuries[(self.injuries['Relinquished'] == self.name) & (self.injuries['Date'] == row.Date)]
                if result.empty == False:
                    injury = injuryScore.regressionCalc(result.Notes)
                else: 
                    injury = 0

                #calculate distance regressor, time regressor, and minutes regressor
                distRegress = injuryScore.distRegressor(dist)
                daysBonus = injuryScore.timeRegressor(days)
                minsRegressor = injuryScore.minsRegress(row.MP[0:2])
                
                #use predetermined weights to calculate health value
                healthValue = values[-1] + (0.33 *  distRegress) + (0.33 *  minsRegressor) + (0.33 * daysBonus) + injury
                #cap value at 1
                if healthValue >= float(1):
                    values.append(1.0)
                else:
                    values.append(healthValue)
                cnt += 1
            else:
                values.append(0.6)
        #remove initial value, add to DF and return important columns
        values = values[1:]
        self.player['Injury and Fatigue Score'] = values
        return self.player[['Rk', 'G', 'Date', 'Injury and Fatigue Score']]
                
