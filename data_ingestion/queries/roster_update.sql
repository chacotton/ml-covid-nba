insert into ACTIVE_ROSTER_DUMMY (PLAYER, GAME_DATE, TEAM, ACTIVE, COVID, MP, PLAYER_ID, HEALTH, IMPACT, SEASON, DISTANCE, PRED_HEALTH)
VALUES (:player, :game_date, :team, :active, :covid, 0, :player_id, :health, -1, :season, :distance, :health);
