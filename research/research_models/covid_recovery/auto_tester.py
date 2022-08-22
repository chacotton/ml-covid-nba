import numpy as np
import pandas as pd
from data.injury_labeller.injuryScore import injuryScore
from data.covid_recovery import Covid
from datetime import datetime, timedelta
from covid_lstm import Serial, Average, FederatedAverage
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt


def plot(ytrue, ypred, file):
    plt.figure()
    plt.plot(ytrue, label='true')
    plt.plot(ypred, label='pred')
    plt.legend()
    plt.savefig(f'{file}.png')


if __name__ == '__main__':
    data = Covid().get_dataset()
    all_tables = []
    lag = 3
    for index, row in data.loc[:,'Activated':'Player_ID'].iterrows():
        if len(row.Player_ID) > 1:
            try:
                year = 2021 if pd.to_datetime(row.Activated) < datetime(2021, 6, 1) else 2022
                table = injuryScore(row.Player_ID, 2021).getInjuryScore()
            except (IndexError, ValueError):
                continue
            table.index = pd.to_datetime(table.Date)
            new_table = table.groupby(table.index).mean().resample('D').interpolate().loc[pd.to_datetime(row.Activated):pd.to_datetime(row.Activated) + timedelta(days=30)]
            new_table['Game'] = 0
            new_table.loc[new_table.index.intersection(table.index), 'Game'] = 1
            if len(new_table) == 31:
                all_tables.append(np.concatenate((np.zeros(shape=(lag, 2)), new_table.values)))
    count = len(all_tables)
    data = np.array(all_tables)
    x_train = data.reshape(count, 31 + lag, 2)[0:-5]
    x_test = data.reshape(count, 31 + lag, 2)[-5:]
    mae = []
    for i, x in enumerate(x_test):
        x[0:lag] = .85
        mae.append(mean_absolute_error(x[:,0][lag:], (np.convolve(x[:,0], np.ones(lag), 'valid') / lag)[:-1]))
        x[0:lag] = 0
        if i == 0:
            plot(x[:,0][lag:], (np.convolve(x[:,0], np.ones(lag), 'valid') / lag)[:-1], file='baseline')
    print(f'Baseline: {sum(mae) / len(mae)}')
    model = Average(neurons=500, lr=.0001)
    model.fit(x_train, lag=lag, epochs=50)
    mae = []
    for i, x in enumerate(x_test):
        mae.append(mean_absolute_error(x[:,0][lag:], model.predict(x).flatten()))
        if i == 0:
            plot(x[:,0][lag:], model.predict(x).flatten(), file='average')
    print(f'Average: {sum(mae)/len(mae)}')
    model = Serial(neurons=500, lr=.0001)
    model.fit(x_train, lag=lag, epochs=50)
    mae = []
    for i, x in enumerate(x_test):
        mae.append(mean_absolute_error(x[:,0][lag:], model.predict(x).flatten()))
        if i == 0:
            plot(x[:,0][lag:], model.predict(x).flatten(), file='serial')
    print(f'Serial: {sum(mae) / len(mae)}')
    model = FederatedAverage(neurons=500, lr=.0001)
    model.fit(x_train, lag=lag, epochs=50)
    mae = []
    for i, x in enumerate(x_test):
        mae.append(mean_absolute_error(x[:,0][lag:], model.predict(x).flatten()))
        if i == 0:
            plot(x[:,0][lag:], model.predict(x).flatten(), file='fed_average')
    print(f'Federated Average: {sum(mae) / len(mae)}')
