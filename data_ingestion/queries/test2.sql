select * from nba.DUMMY_SCHEDULE where GAME_DATE = to_date('2022/01/13', 'yyyy/mm/dd') and HOME = 'Utah Jazz';

merge into nba.DUMMY_SCHEDULE dest
    USING( SELECT to_date('2022/01/13', 'yyyy/mm/dd') game_date, 'Utah Jazz' home, 80 home_pts FROM dual) src
     ON( dest.GAME_DATE = src.game_date and dest.HOME = src.home)
     WHEN MATCHED THEN
       UPDATE SET HOME_PTS = src.home_pts
     WHEN NOT MATCHED THEN
       INSERT( game_date, home, HOME_PTS)
         VALUES( src.game_date, src.home, src.home_pts);