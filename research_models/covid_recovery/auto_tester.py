import numpy as np
import pandas as pd
from data.injury_labeller.injuryScore import injuryScore
from data.covid_recovery import Covid
from datetime import datetime, timedelta
from covid_lstm import Serial, Average, FederatedAverage
from sklearn.metrics import mean_absolute_error


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
            table = table.groupby(table.index).mean().resample('D').interpolate().loc[pd.to_datetime(row.Activated):pd.to_datetime(row.Activated) + timedelta(days=30)]
            if len(table) == 31:
                all_tables.append(np.concatenate((np.zeros(lag), table['Injury and Fatigue Score'].values)))
    count = len(all_tables)
    data = np.array(all_tables)
    x_train = data.reshape(count, 31 + lag, 1)[0:-5]
    x_test = data.reshape(count, 31 + lag, 1)[-5:]
    mae = []
    for x in x_test:
        x[0:lag] = .85
        mae.append(mean_absolute_error(x.flatten()[lag:], (np.convolve(x.flatten(), np.ones(lag), 'valid') / lag)[:-1]))
        x[0:lag] = 0
    print(f'Baseline: {sum(mae) / len(mae)}')
    model = Average(neurons=500, lr=.0001)
    model.fit(x_train, lag=lag, epochs=50)
    mae = []
    for x in x_test:
        mae.append(mean_absolute_error(x.flatten()[lag:], model.predict(x).flatten()))
    print(f'Average: {sum(mae)/len(mae)}')
    model = Serial(neurons=500, lr=.0001)
    model.fit(x_train, lag=lag, epochs=50)
    mae = []
    for x in x_test:
        mae.append(mean_absolute_error(x.flatten()[lag:], model.predict(x).flatten()))
    print(f'Serial: {sum(mae) / len(mae)}')
    model = FederatedAverage(neurons=500, lr=.0001)
    model.fit(x_train, lag=lag, epochs=50)
    mae = []
    for x in x_test:
        mae.append(mean_absolute_error(x.flatten()[lag:], model.predict(x).flatten()))
    print(f'Federated Average: {sum(mae) / len(mae)}')
