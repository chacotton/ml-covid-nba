from typing import Final
from collections import namedtuple

ADJUSTED_SHOOTING_21: Final = 'adjusted_shooting_21'
ADVANCED_21: Final = 'advanced_21'
COVID: Final = 'injury'
PER_GAME: Final = 'per_game_21'
PLAY_BY_PLAY_21: Final = 'play_21'
SHOOTING_21: Final = 'shooting_21'

DataFile = namedtuple("DataFile", "folder file")

files: Final = {
                'adjusted_shooting_21': DataFile('player_data/', 'nba_adjusted_shooting_2021_2022.csv'),
                'advanced_21': DataFile('player_data/', 'nba_advanced_2021_2022.csv'),
                'injury': DataFile('covid_data/', 'NBA_Injury_Data.csv'),
                'per_game_21': DataFile('player_data/', 'nba_per_game_2021_2022.csv'),
                'play_21': DataFile('player_data/', 'nba_play_by_play_2021_2022.csv'),
                'shooting_21': DataFile('player_data/', 'nba_shooting_2021_2022.csv'),
                }

