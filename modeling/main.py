import time
from argparse import ArgumentParser
import mlflow
import pandas as pd
import numpy as np
from datetime import date
from chance_of_victory import NBACoV
from utils import read_table, get_engine, write_db
from tqdm import tqdm


def impact():
    model = NBACoV('/Users/chasecotton/ml-covid-nba/mlflow_utils/classifier_v2')
    rows = read_table(
        'select game_date, player_id, season, team, health, impact from nba.ACTIVE_ROSTER order by PLAYER_ID, GAME_DATE')
    player = ''
    health = 0
    with get_engine().connect() as conn:
        for i, row in tqdm(rows.iterrows(), total=len(rows)):
            if row.player_id != player:
                player = row.player_id
                health = 1
            if row.health == 0:
                health = 1
            elif row.health == health or row.impact != 0:
                continue
            past_df = read_table('impact_table.sql', connection=conn, season=row.season, game_date=row.game_date,
                                 player_id=row.player_id, team=row.team, health=health)
            if past_df.empty:
                continue
            now = read_table('impact_table.sql', connection=conn, season=row.season, game_date=row.game_date,
                             player_id=row.player_id, team=row.team, health=row.health)
            base = model.predict(past_df.iloc[:, 3:])
            new = model.predict(now.iloc[:, 3:])
            if row.team == now.loc[0, 'home']:
                impact = new - base
            else:
                impact = base - new  # (1 - new) - (1 - base) = base - new
            # print(f'{impact} -> ({health},{row.health})')
            health = row.health
            if abs(impact.item()) > .001 and abs(impact.item() - row.impact) > .001:
                # print('write')
                write_db(
                    'update nba.active_roster set impact = :impact where GAME_DATE = :game_date and PLAYER_ID = :player_id',
                    impact=float(impact.item()), game_date=row.game_date, player_id=row.player_id, connection=conn)


if __name__ == '__main__':
    impact()
