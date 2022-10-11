select avg(case when ((HOME_PTS > AWAY_PTS) and (HOME_WIN_PROB > AWAY_WIN_PROB)) or
         ((AWAY_PTS > HOME_PTS) and (AWAY_WIN_PROB > HOME_WIN_PROB)) then 1 else 0 end) as accuracy from NBA.SCHEDULE
where HOME_WIN_PROB > 0 and GAME_DATE >= :start_date and GAME_DATE < :end_date;