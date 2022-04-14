import mlflow
import logging
import sys
import pandas as pd
import numpy as np
from collections import namedtuple
from data.chance_of_victory import WinDataset
from data.covid_recovery import Covid


logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

dataset = namedtuple('dataset', 'data target')
data_attributes = namedtuple('data_attributes', 'file object kwargs target')

atlantic_division = [
    'Boston Celtics',
    'Philadelphia 76ers',
    'Toronto Raptors',
    'Brooklyn Nets',
    'New York Knicks',
]


def setup(models: str = 'experiment'):
    """
    Sets up mysql backend for mlflow if using linux host
    :param models: 'test' or 'experiment'
    :return: None
    :raises: AssertionError if passing invalid models parameter
    """
    assert models in ['test', 'experiment']
    db_uri = f'mysql+pymysql://admin:NBACovid19!@10.0.0.150/{models}_db'
    if sys.platform == 'linux':
        mlflow.set_tracking_uri(db_uri)
    elif sys.platform == 'darwin':
        db_uri = f'mysql+pymysql://admin:NBACovid19!@127.0.0.1:3307/{models}_db'
        mlflow.set_tracking_uri(db_uri)


def test_data(data: str) -> dataset:
    """
    Returns dummy data for type of problem
    :param data: 'ts', 'classification', or 'regression'
    :return: dataset[data: pd.DataFrame, target: str]
    :raises: AssertionError if passing invalid data parameter
    """
    assert data in ['ts', 'classification', 'regression']
    datasets = {
        'ts': data_attributes('covid_dataset', Covid, {}, 'Health'),
        'classification': data_attributes('win_dataset_class', WinDataset, {'problem': 'classification'}, 'Outcome'),
        'regression': data_attributes('win_dataset_reg', WinDataset, {'problem': 'regression'}, 'Points'),
    }
    try:
        df = pd.read_csv(datasets[data].file + '.csv')
    except FileNotFoundError:
        df = datasets[data].object(**datasets[data].kwargs).get_dataset()
        df.to_csv(datasets[data].file + '.csv', index=False)
    return dataset(df, datasets[data].target)


def team_train_test_split(team: str, opponents: list, data: dataset) -> tuple:
    """
    Splits train-test by team
    :param team: str
    :param opponents: list[str]: opponents in test set
    :param data: dataset object
    :return:
    """
    team_data = data.data[data.data.Team == team]
    train = team_data[~team_data.Opponent.isin(opponents)]
    test = team_data[team_data.Opponent.isin(opponents)]
    x_train, y_train = train.drop(['Team', 'Points', 'Opponent'], axis=1), train.pop('Points')
    x_test, y_test = test.drop(['Team', 'Points', 'Opponent'], axis=1), test.pop('Points')
    x_train.Location = x_train.Location.apply(lambda x: 0 if x == 'Away' else 1)
    x_test.Location = x_test.Location.apply(lambda x: 0 if x == 'Away' else 1)
    return x_train, x_test, y_train, y_test
