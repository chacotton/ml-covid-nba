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

# Problem Type
CLASSIFICATION: Final = "classification"
REGRESSION: Final = "regression"

# Files
ADJUSTED_SHOOTING_21: Final = "adjusted_shooting_21"
ADVANCED_21: Final = "advanced_21"
COVID: Final = "injury"
PER_GAME: Final = "per_game_21"
PLAY_BY_PLAY_21: Final = "play_21"
SHOOTING_21: Final = "shooting_21"
GAMES: Final = "games"
TEAM: Final = "team"

# Player Columns
MINUTES: Final = "MP"

# Team Columns
MOV: Final = "MOV"

# Win Dataset Columns
HOME: Final = "Home_pts"
PLAYER: Final = "Away_player_0"
AWAY_END: Final = "Away_player_14"
HOME_START: Final = "Home_player_0"

# Available Player Statistics
FG: Final = "FG"            # Field Goals Made per Game
FGA: Final = "FGA"          # Field Goals Attempted per Game
FGP: Final = "FG%"          # Field Goal Percentage
THP: Final = "3P"           # 3-Pointers Made per Game
THPA: Final = "3PA"         # 3-Pointers Attempted per Game
THPP: Final = "3P%"         # 3-Pointer Percentage
TP: Final = "2P"            # 2-Pointers Made per Game
TPA: Final = "2PA"          # 2-Pointers Attempted per Game
TPP: Final = "2P%"          # 2-Pointer Percentage
EFGP: Final = "eFG%"        # Effective Field Goal Percentage
FT: Final = "FT"            # Free Throws Made per Game
FTA: Final = "FTA"          # Free Throws Attempted per Game
FTP: Final = "FT%"          # Free Throw Percentage
ORB: Final = "ORB"          # Offensive Rebounds per Game
DRB: Final = "DRB"          # Defensive Rebounds per Game
TRB: Final = "TRB"          # Total Rebounds per Game
AST: Final = "AST"          # Assists per Game
STL: Final = "STL"          # Steals per Game
BLK: Final = "BLK"          # Blocks per Game
TOV: Final = "TOV"          # Turnovers per Game
PF: Final = "PF"            # Personal Fouls per Game
PTS: Final = "PTS"          # Points per Game
PER: Final = "PER"          # Player Efficiency Rating
TSP: Final = "TS%"          # True Shooting Percentage
THPAR: Final = "3PAr"       # Three Point Attempt Rate
FTR: Final = "FTr"          # Free Throw Attempt Rate
ORBP: Final = "ORB%"        # Offensive Rebound Percentage
DRBP: Final = "DRB%"        # Defensive Rebound Percentage
TRBP: Final = "TRB%"        # Total Rebound Percentage
ASTP: Final = "AST%"        # Assist Percentage
STLP: Final = "STL%"        # Steal Percentage
BLKP: Final = "BLK%"        # Block Percentage
TOVP: Final = "TOV%"        # Turnover Percentage
USGP: Final = "USG%"        # Usage Percentage
OWS: Final = "OWS"          # Offensive Win Shares
DWS: Final = "DWS"          # Defensive Win Shares
WS: Final = "WS"            # Win Shares
WS48: Final = "WS/48"       # Win Shares per 48 Minutes
OBPM: Final = "OBPM"        # Offensive Box Plus Minus
DBPM: Final = "DBPM"        # Defensive Box Plus Minus
BPM: Final = "BPM"          # Box Plus Minus
VORP: Final = "VORP"        # Value over Replacement Player

# Column Lookup Dict
STATS: Final = {
    FG: PER_GAME,
    FGA: PER_GAME,
    FGP: PER_GAME,
    THP: PER_GAME,
    THPA: PER_GAME,
    THPP: PER_GAME,
    TP: PER_GAME,
    TPA: PER_GAME,
    TPP: PER_GAME,
    EFGP: PER_GAME,
    FT: PER_GAME,
    FTA: PER_GAME,
    FTP: PER_GAME,
    ORB: PER_GAME,
    DRB: PER_GAME,
    TRB: PER_GAME,
    AST: PER_GAME,
    STL: PER_GAME,
    BLK: PER_GAME,
    TOV: PER_GAME,
    PF: PER_GAME,
    PTS: PER_GAME,
    PER: ADVANCED_21,
    TSP: ADVANCED_21,
    THPAR: ADVANCED_21,
    FTR: ADVANCED_21,
    ORBP: ADVANCED_21,
    DRBP: ADVANCED_21,
    TRBP: ADVANCED_21,
    ASTP: ADVANCED_21,
    STLP: ADVANCED_21,
    BLKP: ADVANCED_21,
    TOVP: ADVANCED_21,
    USGP: ADVANCED_21,
    OWS: ADVANCED_21,
    DWS: ADVANCED_21,
    WS: ADVANCED_21,
    WS48: ADVANCED_21,
    OBPM: ADVANCED_21,
    DBPM: ADVANCED_21,
    BPM: ADVANCED_21,
    VORP: ADVANCED_21,
}
