import os
import sys
import contextlib
import numpy as np
from tqdm.auto import tqdm
from sklearn.metrics import mean_absolute_error
from data.covid_recovery import Covid
from data.injury_labeller.injuryScore import injuryScore
from datetime import datetime, timedelta
import torch
from neuralprophet import NeuralProphet
import pandas as pd
from scipy.special import expit
import logging

logging.getLogger('neuralprophet').setLevel(logging.FATAL)


def model_generator(input_length, layers=0, neurons=0, **kwargs):
    model = NeuralProphet(
        growth='off',
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_reg=kwargs.get('seasonality_reg', 1),
        n_lags=input_length,
        n_forecasts=1,
        num_hidden_layers=layers,
        d_hidden=neurons,
        epochs=1,
        batch_size=32,
        newer_samples_weight=kwargs.get('newer_samples_weight', 2.0),
        newer_samples_start=kwargs.get('newer_samples_start', 0.0),
        loss_func=kwargs.get('loss_func', torch.nn.HuberLoss),
        normalize='off',
    )
    return model


class FederatedAverage:

    def __init__(self, neurons=500, layers=0):
        self.model = None
        self.neurons = neurons
        self.lag = None
        self.layers = layers

    def fit(self, data, lag=12, epochs=10, **kwargs):
        assert isinstance(data, list)
        self.lag = lag
        self.model = model_generator(input_length=lag, layers=self.layers, **kwargs)
        models = [model_generator(input_length=lag, layers=self.layers, **kwargs) for _ in range(len(data))]
        season = self.model.season_config
        self.model.fit(data[0])
        #self.model.season_config = season
        for _ in tqdm(range(epochs)):
            for m, x in zip(models, data):
                m.fit(x, freq='D', minimal=True)
                m.season_config = season
            parameters = lambda m: m.model.parameters()
            for params in zip(self.model.model.parameters(), *map(parameters, models)):
                params[0].data = torch.sum(torch.stack(params[1:]), dim=0)
                for p in params[1:]:
                    p.data = params[0]
        return self

    def predict(self, data):
        yhat = np.zeros(31)
        for i in range(31):
            yhat[i] = self.model.predict(self.model.make_future_dataframe(data[:self.lag + i], periods=1)).yhat1.iloc[-1]
        return expit(yhat)


if __name__ == '__main__':
    data = Covid().get_dataset()
    all_tables = []
    lag = 3
    count = 0
    for index, row in data.loc[:, 'Activated':'Player_ID'].iterrows():
        if len(row.Player_ID) > 1:
            try:
                year = 2021 if pd.to_datetime(row.Activated) < datetime(2021, 6, 1) else 2022
                table = injuryScore(row.Player_ID, 2021).getInjuryScore()
            except (IndexError, ValueError):
                continue
            table.index = pd.to_datetime(table.Date)
            table = table.groupby(table.index).mean().resample('D').interpolate().loc[
                    pd.to_datetime(row.Activated):pd.to_datetime(row.Activated) + timedelta(days=30)]
            if len(table) == 31:
                table = pd.concat([pd.DataFrame({'ds': pd.date_range(end=table.index[0] - timedelta(days=1), periods=lag, freq='D'),
                                                 'y': np.zeros(lag)}),
                                   pd.DataFrame({'ds': table.index,
                                                 'y': table['Injury and Fatigue Score']})])
                all_tables.append(table)

    count = len(all_tables)
    x_train = all_tables[:-5]
    x_test = all_tables[-5:]
    mae = []
    model = FederatedAverage(neurons=100, layers=1)
    model.fit(x_train, lag=lag, epochs=100)
    mae = []
    for x in x_test:
        mae.append(mean_absolute_error(x.y.values[lag:], model.predict(x)))
    print(f'Federated Average: {sum(mae) / len(mae)}')