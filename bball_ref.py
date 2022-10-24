import collections
import datetime
from basketball_reference_scraper.injury_report import get_injury_report
class InjuryReport:
    
    def __init__(self):
        self.injuryMapping = get_injury_report()
        self.lastUpdated = datetime.datetime.now()
        
    def refresh(self):
        self.injuryMapping = get_injury_report()
        self.lastUpdated = datetime.datetime.now()
        
        self.injuryMapping = self.injuryMapping[self.injuryMapping.DATE == datetime.date.today().strftime("%Y-%m-%d")]
        print(self.injuryMapping)
    def search(self, playerName):
        if playerName not in self.injuryMapping['PLAYER'].values:
            return True, "Active"
        else:
            return False, self.injuryMapping.loc[self.injuryMapping['PLAYER'] == playerName]['INJURY'].values[0]



#c = InjuryReport().search("Brandon Ingram")
#print(c)