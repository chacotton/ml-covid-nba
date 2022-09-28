from argparse import ArgumentParser
import mlflow
import pandas as pd
import numpy as np
from datetime import date
from chance_of_victory import NBACoV
from utils import read_table, get_engine
from tqdm import tqdm

if __name__ == '__main__':
    model = NBACoV('/Users/chasecotton/ml-covid-nba/mlflow_utils/classifier_v2')
    dates = read_table("select distinct game_date from nba.SCHEDULE where SEASON = 2022").game_date
    with get_engine().begin() as conn:
        for days in tqdm(dates):
            df = model.inference_table(days.date())
            results = model.predict(df.iloc[:, 3:-1])
            probs = {k: v for k, v in zip(df.home.values, results)}
            model.update_table(probs, conn)
