from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score
from urllib.request import urlopen
from bs4 import BeautifulSoup
from haversine import haversine
import pprint
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dropout
import pandas as pd
import requests
from sklearn.model_selection import train_test_split
from matplotlib import pyplot

class injuryScore:

    #define inputs for creating and calculating injury score
    # CSV - CSV of player inputted similar to BBall reference notation
    # name - name of player, use full name from BBall reference
    def __init__(self, CSV, name) -> None:
        self.injuries = pd.read_csv("NBA_Injury_Data.csv")
        df_cities = pd.read_csv("stadiums.csv") 
        self.cities = df_cities[df_cities['League'] == 'NBA']
        self.player = pd.read_csv(CSV)
        self.name = name
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
    https://towardsdatascience.com/realigning-sports-leagues-with-a-clustering-algorithm-d6e9de9294d0
    '''
    #calculates distance based on mathematical latitude and longitudinal calculations
    def dist(lat1, long1, lat2, long2):
        
        lat1, lat2 = np.deg2rad(lat1), np.deg2rad(lat2)
        long1, long2 = np.deg2rad(long1), np.deg2rad(long2)
        EARTH_RADIUS = 3958.8
        return EARTH_RADIUS * np.arccos((np.sin(lat1) * np.sin(lat2)) + 
                            np.cos(lat1) * np.cos(lat2) * np.cos(long2 - long1))
    
    #calculate distance with Haversine
    def calcDist(start, end):
        start_long = injuryScore.cities.loc[injuryScore.cities.Team == injuryScore.teams_expanded[start], 'Long'].tolist()[0]
        start_lat = injuryScore.cities.loc[injuryScore.cities.Team == injuryScore.teams_expanded[start], 'Lat'].tolist()[0]
        end_long = injuryScore.cities.loc[injuryScore.cities.Team == injuryScore.teams_expanded[end], 'Long'].tolist()[0]
        end_lat = injuryScore.cities.loc[injuryScore.cities.Team == injuryScore.teams_expanded[end], 'Lat'].tolist()[0]
        return haversine((start_lat, start_long),(end_lat, end_long), unit='mi')
    
    #injury calculations based on labels
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

    #get difference in day
    def getDayDiff(day1, day2): 
        x = datetime.strptime(day1, "%Y-%m-%d")
        y = datetime.strptime(day2, "%Y-%m-%d")
        return (x-y).days

    #calculate injury score based on weights and flat injury for a given season
    def getInjuryScore():
        prevLoc = ''
        
        prevDate = injuryScore.player['Date'].iloc[0]
        print(prevDate)
        if injuryScore.player['Date'].iloc[0] == None:
            prevLoc = injuryScore.player['Home'].iloc[0]
        else: 
            prevLoc = injuryScore.player['Opp'].iloc[0]
        cnt = 0
        values = []
        values.append(1)
        for row in injuryScore.player.itertuples():
            if row.MP[0:2] != 'In' and row.MP[0:2] != 'Di':
                if values[-1] == 0.6: 
                    values[-1] = 0.8
                if row.Home == '@':
                    dist = injuryScore.calcDist(prevLoc, row.Opp)
                    prevLoc = row.Opp
                else:
                    dist = injuryScore.calcDist(prevLoc, row.Tm)
                    prevLoc = row.Tm


                days = injuryScore.getDayDiff(row.Date, prevDate)
                prevDate = row.Date
                minutes = row.MP[0:2]

                result = injuryScore.injuries[(injuryScore.injuries['Relinquished'] == name) & (injuries['Date'] == row.Date)]
                if result.empty == False:
                    injury = injuryScore.regressionCalc(result.Notes)
                else: 
                    injury = 0
            

                if dist == 0:
                    distRegress = 0.10
                elif dist < 1000:
                    distRegress = -0.10
                elif dist < 2000:
                    distRegress = -0.15
                else: 
                    distRegress = -0.20
                if days == 1:
                    daysBonus = 0
                elif days == 2:
                    daysBonus = 0.05
                elif days == 3: 
                    daysBonus = 0.10
                else:
                    daysBonus = 0.15
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
                
                healthValue = values[-1] + (0.33 *  distRegress) + (0.33 *  minsRegressor) + (0.33 * daysBonus) + injury
                if healthValue >= float(1):
                    values.append(1.0)
                else:
                    values.append(healthValue)
                cnt += 1
            else:
                values.append(0.6)
        values = values[1:]
        injuryScore.player['Injury and Fatigue Score'] = values
        return injuryScore.player
                
