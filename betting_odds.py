# koushik's API KEY -> 4c8d5187697efaecc1a8815a992519d5
import requests


class VegasOdds:
    
    def __init__(self, api_key):
        self.api_key = api_key

    def getOdds(self):
        dailyOdds = {}
        sports_response = requests.get(
        'https://api.the-odds-api.com/v4/sports/basketball_nba/odds/', 
        params={
        'api_key': self.api_key,
        'regions': "us",
        'markets': "spreads",
        }
        )
        #print(len(sports_response.json()))
        for i in range(0, len(sports_response.json())):
            #print(sports_response.json()[i]['bookmakers'][0]['markets'][0]['outcomes'])
            base = sports_response.json()[i]['bookmakers'][0]['markets'][0]['outcomes']
            for j in range(len(base)):
                dailyOdds[base[j]['name']] = base[j]['point']
        #print(dailyOdds)
        return dailyOdds
        

'''
c = VegasOdds('4c8d5187697efaecc1a8815a992519d5')
c.getOdds()
'''