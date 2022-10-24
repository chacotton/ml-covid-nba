
games_date = "SELECT GAME_DATE, HOME, AWAY FROM NBA.SCHEDULE WHERE GAME_DATE = :today"

old_player = "SELECT player_id, pts, orb, ast from NBA.PLAYER_STATS where PLAYER_ID = :player"

new_player = "SELECT player_id, pts, orb, ast from NBA.DUMMY_PLAYER_STATS where PLAYER_ID = :player"

random_player = "SELECT player_id FROM ACTIVE_ROSTER_DUMMY where GAME_DATE = :game_date and ACTIVE = 1 and MP > 15"

games = "SELECT game_date FROM nba.ACTIVE_ROSTER_DUMMY where PLAYER_ID = :player_id and ACTIVE = 1 order by 1"
