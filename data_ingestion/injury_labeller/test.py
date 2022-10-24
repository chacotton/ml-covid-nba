
import sys
sys.path.append("/Users/koushikchennakesavan/Documents/EE364D/ml-covid-nba/")
from injuryScore import InjuryScore
#c = injuryScore.injuryScore("embiijo01", 2021)
c = InjuryScore("Joel Embiid", 2020).getInjuryScore()
print(c.head(45))