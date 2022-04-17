import pandas as pd
from data import Dataset
from data.constants import *
from data import covid_recovery


df = covid_recovery.Covid()._covid_dataset()
print(df)

def test_init():
    df = covid_recovery.Covid().get_dataset()
    assert isinstance(df ,pd.DataFrame) is True
def test_cols():
    df = covid_recovery.Covid().get_dataset()
    assert df.shape[1] == 5
def test_rows():
    df = covid_recovery.Covid().get_dataset()
    assert df.shape[0] == 501
def test_recovery():
    df = covid_recovery.Covid()._covid_dataset()
    print(df)
    assert isinstance(df ,pd.DataFrame) is True
def test_recovery_cols():
    df = covid_recovery.Covid()._covid_dataset()
    print(df)
    result = df[df.Deactivated > df.Activated]
    assert result.empty is True
def create_dataset():
    df = covid_recovery.Covid()._create_dataset()
    assert isinstance(df ,pd.DataFrame) is True