select minutes/total_mins from
(select (W+L)*48*5 as total_mins from TEAM_STATS where TEAM = :team and SEASON = :season) t2,
(select sum(mp) as minutes from PLAYER_STATS where PLAYER_ID in (:a1, :a2, :a3, :a4, :a5, :a6, :a7, :a8, :a9, :a10, :a11, :a12, :a13, :a14) and SEASON = :season) t1