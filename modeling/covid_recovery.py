from modeling import NBAModel
import pandas as pd
import numpy as np
import torch
from modeling.utils import read_table
from datetime import timedelta, date


class NBACovid(NBAModel):
    """
    Class Implementation of NBA Covid Recovery Model

    Loads Covid Recovery Model and writes prediction to database
    """

    cols = ['health', 'distance', 'mp', 'active', 'covid']
    MINUTES_MAX = 48
    DIST_MAX = 3813.715405952134
    INFERENCE = "select game_date, health, distance, mp, active, covid from ACTIVE_ROSTER_DUMMY where PLAYER_ID = :player_id and GAME_DATE <= :game_date order by 1"
    monitoring_query = 'health_monitor.sql'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input_width = self.model.input_chunk_length

    @staticmethod
    def _load_model(model_file: str):
        """
        overloads base class method to support pytorch loading, mlflow loading is not efficient enough
        :param model_file: file path
        :return: pytorch model
        """
        return torch.load(model_file).model

    def single_predict(self, x: pd.DataFrame) -> float:
        """
        shapes data and returns single prediction values
        :param x: input date
        :return: float
        """
        return self.model((torch.DoubleTensor(x[-self.input_width:].values.reshape(1, -1)),
                           0)).detach().numpy().flatten().clip(0, 1).item()

    def load_data(self, game_date: date, player_id: str) -> pd.DataFrame:
        """
        reads inference table from database
        :param game_date: date object specifying target date for prediction
        :param player_id: player to get table for
        :return: pd.DataFrame of inference input data
        """
        return read_table(self.INFERENCE, game_date=game_date, player_id=player_id, index_col='game_date')

    def _preprocess(self, x: pd.DataFrame) -> tuple:
        """
        performs data processing to make prediction
        :param x: pd.DataFrame
        :return: pd.DataFrame, target date
        """
        x.distance = x.distance.shift(-1)
        end_date = x.index[-1]
        x.drop(end_date, axis=0, inplace=True)
        x.distance /= self.DIST_MAX
        x.mp /= self.MINUTES_MAX
        x = x.resample('D').asfreq()
        x.health = x.health.interpolate()
        x.fillna(0, inplace=True)
        return x, end_date

    def predict(self, x: pd.DataFrame) -> float:
        """
        prediction function, returns single prediction value
        :param x: pd.DataFrame of inference data
        :return: floating point prediction between [0,1]
        """
        x, end_date = self._preprocess(x)
        if x.index.empty:
            return 1
        start_date = x.index[-1]
        for i in range((end_date - start_date).days):
            if (extra := (21 - len(x))) > 0:
                extra_days = pd.DataFrame(np.array([1, 0, 0, 0, 0]*extra).reshape(-1, 5),
                                          columns=self.cols,
                                          index=pd.date_range(end=x.index[0]-timedelta(days=1), freq='D', periods=extra))
                x = pd.concat((extra_days, x))
            yhat = self.single_predict(x.iloc[-21:, :])
            row = pd.DataFrame([[yhat, 0, 0, 0, 0]], columns=self.cols, index=[start_date + timedelta(days=1)])
            x = pd.concat((x, row), axis=0)
        return x.health[-1]

