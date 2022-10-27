try:
    from typing import Final
except ImportError:
    from typing import TypeVar
    Final = TypeVar('Final')

TEAMS: Final = {
     'Dallas Mavericks': 'DAL',
     'Orlando Magic': 'ORL',
     'San Antonio Spurs': 'SAS',
     'Denver Nuggets': 'DEN',
     'Brooklyn Nets': 'BRK',
     'Utah Jazz': 'UTA',
     'Washington Wizards': 'WAS',
     'Golden State Warriors': 'GSW',
     'Los Angeles Clippers': 'LAC',
     'Los Angeles Lakers': 'LAL',
     'Memphis Grizzlies': 'MEM',
     'Milwaukee Bucks': 'MIL',
     'Phoenix Suns': 'PHO',
     'Miami Heat': 'MIA',
     'Indiana Pacers': 'IND',
     'Sacramento Kings': 'SAC',
     'Detroit Pistons': 'DET',
     'Philadelphia 76ers': 'PHI',
     'New York Knicks': 'NYK',
     'Portland Trail Blazers': 'POR',
     'Oklahoma City Thunder': 'OKC',
     'Cleveland Cavaliers': 'CLE',
     'Toronto Raptors': 'TOR',
     'New Orleans Pelicans': 'NOP',
     'Charlotte Hornets': 'CHO',
     'Atlanta Hawks': 'ATL',
     'Minnesota Timberwolves': 'MIN',
     'Boston Celtics': 'BOS',
     'Houston Rockets': 'HOU',
     'Chicago Bulls': 'CHI'
}

# Short Queries
games_today = "SELECT GAME_DATE, HOME, AWAY FROM NBA.SCHEDULE WHERE GAME_DATE = :today"
active_players = "select player_id from ACTIVE_ROSTER_DUMMY where GAME_DATE = :game_date and ACTIVE = 1"
pie_lookup = "select player_id, pie from PLAYER_STATS where SEASON = :season"
actives_update = "update active_roster_dummy set mp = :mp where PLAYER_ID = :player_id and GAME_DATE = :game_date"
char_replace = str.maketrans({'0': 'Z', '1': 'O', '2': 'T', '3': 'H', '%': 'P', '+': 'L', '-': 'M', '/': 'S',
                              '.': 'D', '#': 'N'})
player_to_id = "SELECT player_id, name from nba.PLAYER_IDS"
schedule_update = "UPDATE NBA.SCHEDULE SET HOME_PTS = :home_pts, AWAY_PTS = :away_pts, " \
                  "POINT_DIFFERENCE = :diff, WINNER = :winner where GAME_DATE = :game_date and HOME = :home"
