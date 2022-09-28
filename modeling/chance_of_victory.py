from modeling import NBAModel
import pandas as pd
from datetime import date
from modeling.utils import read_table, write_db


class NBACoV(NBAModel):
    """
    Class Implementation of NBA Chance of Victory Model

    Loads Chance of Victory Model and writes prediction to database
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_date = None

    def inference_table(self, game_date: date = None, season: int = None):
        self.game_date = date.today() if game_date is None else game_date
        if season is None:
            season = self.game_date.year if self.game_date.month < 7 else self.game_date.year + 1
            if season > date.today().year and self.game_date.month < 12:
                season -= 1     # need to use past season stats until enough days have been accumulated
        df = read_table('inference_table.sql', game_date=game_date, season=season)
        return df

    def update_table(self, win_probs: dict, conn):
        query_vars = {'game_date': self.game_date}
        for home, home_win in win_probs.items():
            kwargs = {**query_vars, 'home': home, 'home_win': float(home_win), 'away_win': float(1 - home_win)}
            write_db('win_inference_update.sql', connection=conn, **kwargs)

    def predict(self, x: pd.DataFrame):
        result = self.model.predict(x)
        return result

