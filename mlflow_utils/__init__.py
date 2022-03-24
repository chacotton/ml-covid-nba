import mlflow
import logging
import sys
import pandas as pd
import numpy as np


logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


def setup(models: str = 'test'):
    """
    Sets up mysql backend for mlflow if using linux host
    :param models: 'test', 'covid', or 'win'
    :return: None
    :raises: AssertionError if passing invalid models parameter
    """
    assert models in ['test', 'covid', 'win']
    db_uri = f'mysql+pymysql://admin:NBACovid19!@10.0.0.150/{models}_db'
    if sys.platform == 'linux':
        mlflow.set_tracking_uri(db_uri)
    elif sys.platform == 'darwin':
        db_uri = f'mysql+pymysql://admin:NBACovid19!@127.0.0.1:3307/{models}_db'
        mlflow.set_tracking_uri(db_uri)


def test_data(data: str) -> pd.DataFrame:
    """
    Returns dummy data for type of problem
    :param data: 'ts', 'class', or 'reg'
    :return: pd.DataFrame
    :raises: AssertionError if passing invalid data parameter
    """
    assert data in ['ts', 'class', 'reg']
    if data == 'ts':
        df = pd.DataFrame(columns={'timestamp', 'target', 'other'})
        df.timestamp = pd.date_range('01-01-1970', periods=1000, freq='D')
        df.target = np.sin(np.linspace(0,100,1000))
        df.other = np.cos(np.linspace(0,100,1000))
    elif data == 'class':
        df = pd.DataFrame(columns={'x0', 'x1', 'x2', 'target'})
        df.target = np.random.binomial(1, .5, 1000)
        df.x0 = np.random.normal(0, 1, 1000)
        df.x1 = 10 * np.random.random(1000)
        df.x2 = np.random.randint(20, 25, 1000)
    else:
        df = pd.DataFrame(columns={'x0', 'x1', 'x2', 'target'})
        df.target = np.random.normal(0, 100, 1000)
        df.x0 = np.random.binomial(1, .5, 1000)
        df.x1 = 10 * np.random.random(1000)
        df.x2 = np.random.randint(20, 25, 1000)
    return df
