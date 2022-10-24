select regr_r2(HEALTH, PRED_HEALTH) as r2 from active_roster_dummy where GAME_DATE >= :start_date and GAME_DATE < :end_date
