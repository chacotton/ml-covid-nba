select (t1.home_correct + t1.away_correct) / t1.total as "Total Accuracy",
       (t2.home_correct + t2.away_correct) / t2.total as "60% Win Probability Performance",
       (t3.home_correct + t3.away_correct) / t3.total as "70% Win Probability Performance",
       (t4.home_correct + t4.away_correct) / t4.total as "80% Win Probability Performance",
       (t5.home_correct + t5.away_correct) / t5.total as "90% Win Probability Performance"
from (
select count(case when (HOME_PTS > AWAY_PTS) and (HOME_WIN_PROB > .5) then 1 end) as home_correct,
       count(case when (AWAY_PTS > HOME_PTS) and (AWAY_WIN_PROB > .5) then 1 end) as away_correct,
       count(case when HOME_WIN_PROB > .5 or AWAY_WIN_PROB > .5 then 1 end) as total
from NBA.SCHEDULE) t1,
(select count(case when (HOME_PTS > AWAY_PTS) and (HOME_WIN_PROB > .6) then 1 end) as home_correct,
       count(case when (AWAY_PTS > HOME_PTS) and (AWAY_WIN_PROB > .6) then 1 end) as away_correct,
       count(case when HOME_WIN_PROB > .6 or AWAY_WIN_PROB > .6 then 1 end) as total
from NBA.SCHEDULE) t2,
(select count(case when (HOME_PTS > AWAY_PTS) and (HOME_WIN_PROB > .7) then 1 end) as home_correct,
       count(case when (AWAY_PTS > HOME_PTS) and (AWAY_WIN_PROB > .7) then 1 end) as away_correct,
       count(case when HOME_WIN_PROB > .7 or AWAY_WIN_PROB > .7 then 1 end) as total
from NBA.SCHEDULE) t3,
(select count(case when (HOME_PTS > AWAY_PTS) and (HOME_WIN_PROB > .8) then 1 end) as home_correct,
       count(case when (AWAY_PTS > HOME_PTS) and (AWAY_WIN_PROB > .8) then 1 end) as away_correct,
       count(case when HOME_WIN_PROB > .8 or AWAY_WIN_PROB > .8 then 1 end) as total
from NBA.SCHEDULE) t4,
(select count(case when (HOME_PTS > AWAY_PTS) and (HOME_WIN_PROB > .9) then 1 end) as home_correct,
       count(case when (AWAY_PTS > HOME_PTS) and (AWAY_WIN_PROB > .9) then 1 end) as away_correct,
       count(case when HOME_WIN_PROB > .9 or AWAY_WIN_PROB > .9 then 1 end) as total
from NBA.SCHEDULE) t5;