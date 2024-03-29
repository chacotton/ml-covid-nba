select GAME_DATE, AWAY, HOME,
       haversine(LAT, "LONG", lag(LAT) over (order by GAME_DATE), lag("LONG") over (order by GAME_DATE)) as dist
from nba.SCHEDULE
inner join nba.STADIUMS on SCHEDULE.HOME = STADIUMS.TEAM where (HOME = :team or AWAY = :team) and SEASON = :season and
                                                               GAME_DATE between :date_range and :target_date;