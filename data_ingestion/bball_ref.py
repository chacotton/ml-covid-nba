import datetime
import pandas as pd
from data_ingestion.stat_utils import read_html
from data_ingestion.constants import TEAMS


class InjuryReport:
    
    def __init__(self):
        self.injury_mapping = self.get_injury_report()
        self.last_updated = datetime.datetime.now()

    @staticmethod
    def _break_apart(desc):
        injury, description = desc.split(' - ')
        status, injury = injury.split(' (')
        return status, injury[:-1], description

    @staticmethod
    def get_injury_report():
        table = read_html("https://www.basketball-reference.com/friv/injuries.fcgi#injuries")
        pids = read_html('https://www.basketball-reference.com/friv/injuries.fcgi#injuries', extract_links='all')
        table.index = pids.iloc[:, 0].apply(lambda x: x[1].split('/')[-1][:-5])
        table.index.name = "player_id"
        table[['Status', 'Injury', 'Description']] = pd.DataFrame(table.Description.apply(
                                                     InjuryReport._break_apart).tolist(), index=table.index)
        return table

    def refresh(self):
        self.injury_mapping = self.get_injury_report()
        self.last_updated = datetime.datetime.now()
        self.injury_mapping = self.injury_mapping[self.injury_mapping.DATE == datetime.date.today().strftime("%Y-%m-%d")]

    def search(self, player_name):
        if player_name not in self.injury_mapping['PLAYER'].values:
            return True, "Active"
        else:
            return False, self.injury_mapping.loc[self.injury_mapping['PLAYER'] == player_name]['INJURY'].values[0]

    def team_actives(self, team):
        team_abbrv = TEAMS[team]
        link = f"https://www.basketball-reference.com/teams/{team_abbrv}/2023.html#roster"
        table = read_html(link)
        pids = read_html(link, extract_links='all')
        table.index = pids.iloc[:, 1].apply(lambda x: x[1].split('/')[-1][:-5])
        table.index.name = "player_id"
        table = table[~table["No."].isna()][["Player"]]
        table = pd.merge(table, self.injury_mapping[self.injury_mapping.Status == 'Out'],
                         how='left', left_index=True, right_index=True, suffixes=('', '_x'))
        table = table[table.Injury.isna()][["Player"]].rename({'Player': 'player'}, axis=1)
        table["team"] = team
        table["mp"], table["active"], table["covid"], table["health"] = [0, 1, 0, -1]
        return table.reset_index()
