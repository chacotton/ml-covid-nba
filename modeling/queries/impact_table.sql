select  t1.game_date,
        t1.home,
        t1.away,
        t1."W/L%_HOME",
        t1."MOV_HOME",
        t1."ORTG_HOME",
        t1."DRTG_HOME",
        t1."NRTG_HOME",
        t1."MOV/A_HOME",
        t1."ORtg/A_HOME",
        t1."DRtg/A_HOME",
        t1."NRtg/A_HOME",
        t1."eFG_HOME",
        t1."TS_HOME",
        t1."FTr_HOME",
        t1."3PAr_HOME",
        t1."FG+_HOME",
        t1."2P+_HOME",
        t1."3P+_HOME",
        t1."eFG+_HOME",
        t1."FT+_HOME",
        t1."TS+_HOME",
        t1."FTr+_HOME",
        t1."3PAr+_HOME",
        t1."FG_Add_HOME",
        t1."TS_Add_HOME",
        t1."PER_HOME",
        t1."TS%_HOME",
        t1."ORB%_HOME",
        t1."DRB%_HOME",
        t1."TRB%_HOME",
        t1."AST%_HOME",
        t1."STL%_HOME",
        t1."BLK%_HOME",
        t1."TOV%_HOME",
        t1."USG%_HOME",
        t1."OWS_HOME",
        t1."DWS_HOME",
        t1."WS_HOME",
        t1."WS/48_HOME",
        t1."OBPM_HOME",
        t1."DBPM_HOME",
        t1."BPM_HOME",
        t1."VORP_HOME",
        t1."FG_HOME",
        t1."FGA_HOME",
        t1."FG%_HOME",
        t1."3P_HOME",
        t1."3PA_HOME",
        t1."3P%_HOME",
        t1."2P_HOME",
        t1."2PA_HOME",
        t1."2P%_HOME",
        t1."eFG%_HOME",
        t1."FT_HOME",
        t1."FTA_HOME",
        t1."FT%_HOME",
        t1."ORB_HOME",
        t1."DRB_HOME",
        t1."TRB_HOME",
        t1."AST_HOME",
        t1."STL_HOME",
        t1."BLK_HOME",
        t1."TOV_HOME",
        t1."PF_HOME",
        t1."PTS_HOME",
        t1."PE_PG%_HOME",
        t1."PE_SG%_HOME",
        t1."PE_SF%_HOME",
        t1."PE_PF%_HOME",
        t1."PE_C%_HOME",
        t1."+/-_OnCourt_HOME",
        t1."+/-_On-Off_HOME",
        t1."TO_BadPass_HOME",
        t1."TO_LostBall_HOME",
        t1."Shoot_Fl_Com_HOME",
        t1."Off._Fl_Com_HOME",
        t1."Shoot_Fl_Drn_HOME",
        t1."Off._Fl_Drn_HOME",
        t1."PGA_HOME",
        t1."And1_HOME",
        t1."Blkd_HOME",
        t1."Dist_HOME",
        t1."2P_FGA%_HOME",
        t1."0-3ft_FGA%_HOME",
        t1."3-10_FGA%_HOME",
        t1."10-16ft_FGA%_HOME",
        t1."16-3Pft_FGA%_HOME",
        t1."3P_FGA%_HOME",
        t1."2P_FG%_HOME",
        t1."0-3_FG%_HOME",
        t1."3-10_FG%_HOME",
        t1."10-16_FG%_HOME",
        t1."16-3P_FG%_HOME",
        t1."3P_FG%_HOME",
        t1."2P_FG_AST%_HOME",
        t1."3P_FG_AST%_HOME",
        t1."%FGA_DUNK_HOME",
        t1."#_DUNK_HOME",
        t1."%3PA_HOME",
        t1."Att_Heave_HOME",
        t1."#_Heave_HOME",
        t2."W/L%_AWAY",
        t2."MOV_AWAY",
        t2."ORTG_AWAY",
        t2."DRTG_AWAY",
        t2."NRTG_AWAY",
        t2."MOV/A_AWAY",
        t2."ORtg/A_AWAY",
        t2."DRtg/A_AWAY",
        t2."NRtg/A_AWAY",
        t2."eFG_AWAY",
        t2."TS_AWAY",
        t2."FTr_AWAY",
        t2."3PAr_AWAY",
        t2."FG+_AWAY",
        t2."2P+_AWAY",
        t2."3P+_AWAY",
        t2."eFG+_AWAY",
        t2."FT+_AWAY",
        t2."TS+_AWAY",
        t2."FTr+_AWAY",
        t2."3PAr+_AWAY",
        t2."FG_Add_AWAY",
        t2."TS_Add_AWAY",
        t2."PER_AWAY",
        t2."TS%_AWAY",
        t2."ORB%_AWAY",
        t2."DRB%_AWAY",
        t2."TRB%_AWAY",
        t2."AST%_AWAY",
        t2."STL%_AWAY",
        t2."BLK%_AWAY",
        t2."TOV%_AWAY",
        t2."USG%_AWAY",
        t2."OWS_AWAY",
        t2."DWS_AWAY",
        t2."WS_AWAY",
        t2."WS/48_AWAY",
        t2."OBPM_AWAY",
        t2."DBPM_AWAY",
        t2."BPM_AWAY",
        t2."VORP_AWAY",
        t2."FG_AWAY",
        t2."FGA_AWAY",
        t2."FG%_AWAY",
        t2."3P_AWAY",
        t2."3PA_AWAY",
        t2."3P%_AWAY",
        t2."2P_AWAY",
        t2."2PA_AWAY",
        t2."2P%_AWAY",
        t2."eFG%_AWAY",
        t2."FT_AWAY",
        t2."FTA_AWAY",
        t2."FT%_AWAY",
        t2."ORB_AWAY",
        t2."DRB_AWAY",
        t2."TRB_AWAY",
        t2."AST_AWAY",
        t2."STL_AWAY",
        t2."BLK_AWAY",
        t2."TOV_AWAY",
        t2."PF_AWAY",
        t2."PTS_AWAY",
        t2."PE_PG%_AWAY",
        t2."PE_SG%_AWAY",
        t2."PE_SF%_AWAY",
        t2."PE_PF%_AWAY",
        t2."PE_C%_AWAY",
        t2."+/-_OnCourt_AWAY",
        t2."+/-_On-Off_AWAY",
        t2."TO_BadPass_AWAY",
        t2."TO_LostBall_AWAY",
        t2."Shoot_Fl_Com_AWAY",
        t2."Off._Fl_Com_AWAY",
        t2."Shoot_Fl_Drn_AWAY",
        t2."Off._Fl_Drn_AWAY",
        t2."PGA_AWAY",
        t2."And1_AWAY",
        t2."Blkd_AWAY",
        t2."Dist_AWAY",
        t2."2P_FGA%_AWAY",
        t2."0-3ft_FGA%_AWAY",
        t2."3-10_FGA%_AWAY",
        t2."10-16ft_FGA%_AWAY",
        t2."16-3Pft_FGA%_AWAY",
        t2."3P_FGA%_AWAY",
        t2."2P_FG%_AWAY",
        t2."0-3_FG%_AWAY",
        t2."3-10_FG%_AWAY",
        t2."10-16_FG%_AWAY",
        t2."16-3P_FG%_AWAY",
        t2."3P_FG%_AWAY",
        t2."2P_FG_AST%_AWAY",
        t2."3P_FG_AST%_AWAY",
        t2."%FGA_DUNK_AWAY",
        t2."#_DUNK_AWAY",
        t2."%3PA_AWAY",
        t2."Att_Heave_AWAY",
        t2."#_Heave_AWAY"
from (select schedule.game_date as game_date,
    schedule.home as home,
    schedule.away as away,
    avg(team_stats."W/L%") as "W/L%_HOME",
    avg(team_stats.MOV) as "MOV_HOME",
    avg(team_stats.ORTG) as "ORTG_HOME",
    avg(team_stats.DRTG) as "DRTG_HOME",
    avg(team_stats.NRTG) as "NRTG_HOME",
    avg(team_stats."MOV/A") as "MOV/A_HOME",
    avg(team_stats."ORtg/A") as "ORtg/A_HOME",
    avg(team_stats."DRtg/A") as "DRtg/A_HOME",
    avg(team_stats."NRtg/A") as "NRtg/A_HOME",
sum(active_roster.adj_health * player_stats.eFG) as "eFG_HOME",
sum(active_roster.adj_health * player_stats.TS) as "TS_HOME",
sum(active_roster.adj_health * player_stats.FTr) as "FTr_HOME",
sum(active_roster.adj_health * player_stats."3PAr") as "3PAr_HOME",
sum(active_roster.adj_health * player_stats."FG+") as "FG+_HOME",
sum(active_roster.adj_health * player_stats."2P+") as "2P+_HOME",
sum(active_roster.adj_health * player_stats."3P+") as "3P+_HOME",
sum(active_roster.adj_health * player_stats."eFG+") as "eFG+_HOME",
sum(active_roster.adj_health * player_stats."FT+") as "FT+_HOME",
sum(active_roster.adj_health * player_stats."TS+") as "TS+_HOME",
sum(active_roster.adj_health * player_stats."FTr+") as "FTr+_HOME",
sum(active_roster.adj_health * player_stats."3PAr+") as "3PAr+_HOME",
sum(active_roster.adj_health * player_stats.FG_Add) as "FG_Add_HOME",
sum(active_roster.adj_health * player_stats.TS_Add) as "TS_Add_HOME",
sum(active_roster.adj_health * player_stats.PER) as "PER_HOME",
sum(active_roster.adj_health * player_stats."TS%") as "TS%_HOME",
sum(active_roster.adj_health * player_stats."ORB%") as "ORB%_HOME",
sum(active_roster.adj_health * player_stats."DRB%") as "DRB%_HOME",
sum(active_roster.adj_health * player_stats."TRB%") as "TRB%_HOME",
sum(active_roster.adj_health * player_stats."AST%") as "AST%_HOME",
sum(active_roster.adj_health * player_stats."STL%") as "STL%_HOME",
sum(active_roster.adj_health * player_stats."BLK%") as "BLK%_HOME",
sum(active_roster.adj_health * player_stats."TOV%") as "TOV%_HOME",
sum(active_roster.adj_health * player_stats."USG%") as "USG%_HOME",
sum(active_roster.adj_health * player_stats.OWS) as "OWS_HOME",
sum(active_roster.adj_health * player_stats.DWS) as "DWS_HOME",
sum(active_roster.adj_health * player_stats.WS) as "WS_HOME",
sum(active_roster.adj_health * player_stats."WS/48") as "WS/48_HOME",
sum(active_roster.adj_health * player_stats.OBPM) as "OBPM_HOME",
sum(active_roster.adj_health * player_stats.DBPM) as "DBPM_HOME",
sum(active_roster.adj_health * player_stats.BPM) as "BPM_HOME",
sum(active_roster.adj_health * player_stats.VORP) as "VORP_HOME",
sum(active_roster.adj_health * player_stats.FG) as "FG_HOME",
sum(active_roster.adj_health * player_stats.FGA) as "FGA_HOME",
sum(active_roster.adj_health * player_stats."FG%") as "FG%_HOME",
sum(active_roster.adj_health * player_stats."3P") as "3P_HOME",
sum(active_roster.adj_health * player_stats."3PA") as "3PA_HOME",
sum(active_roster.adj_health * player_stats."3P%") as "3P%_HOME",
sum(active_roster.adj_health * player_stats."2P") as "2P_HOME",
sum(active_roster.adj_health * player_stats."2PA") as "2PA_HOME",
sum(active_roster.adj_health * player_stats."2P%") as "2P%_HOME",
sum(active_roster.adj_health * player_stats."eFG%") as "eFG%_HOME",
sum(active_roster.adj_health * player_stats."FT") as "FT_HOME",
sum(active_roster.adj_health * player_stats."FTA") as "FTA_HOME",
sum(active_roster.adj_health * player_stats."FT%") as "FT%_HOME",
sum(active_roster.adj_health * player_stats."ORB") as "ORB_HOME",
sum(active_roster.adj_health * player_stats."DRB") as "DRB_HOME",
sum(active_roster.adj_health * player_stats."TRB") as "TRB_HOME",
sum(active_roster.adj_health * player_stats."AST") as "AST_HOME",
sum(active_roster.adj_health * player_stats."STL") as "STL_HOME",
sum(active_roster.adj_health * player_stats."BLK") as "BLK_HOME",
sum(active_roster.adj_health * player_stats."TOV") as "TOV_HOME",
sum(active_roster.adj_health * player_stats."PF") as "PF_HOME",
sum(active_roster.adj_health * player_stats."PTS") as "PTS_HOME",
sum(active_roster.adj_health * player_stats."PE_PG%") as "PE_PG%_HOME",
sum(active_roster.adj_health * player_stats."PE_SG%") as "PE_SG%_HOME",
sum(active_roster.adj_health * player_stats."PE_SF%") as "PE_SF%_HOME",
sum(active_roster.adj_health * player_stats."PE_PF%") as "PE_PF%_HOME",
sum(active_roster.adj_health * player_stats."PE_C%") as "PE_C%_HOME",
sum(active_roster.adj_health * player_stats."+/-_OnCourt") as "+/-_OnCourt_HOME",
sum(active_roster.adj_health * player_stats."+/-_On-Off") as "+/-_On-Off_HOME",
sum(active_roster.adj_health * player_stats.TO_BadPass) as "TO_BadPass_HOME",
sum(active_roster.adj_health * player_stats.TO_LostBall) as "TO_LostBall_HOME",
sum(active_roster.adj_health * player_stats.Shoot_Fl_Com) as "Shoot_Fl_Com_HOME",
sum(active_roster.adj_health * player_stats."Off._Fl_Com") as "Off._Fl_Com_HOME",
sum(active_roster.adj_health * player_stats.Shoot_Fl_Drn) as "Shoot_Fl_Drn_HOME",
sum(active_roster.adj_health * player_stats."Off._Fl_Drn") as "Off._Fl_Drn_HOME",
sum(active_roster.adj_health * player_stats."PGA") as "PGA_HOME",
sum(active_roster.adj_health * player_stats.And1) as "And1_HOME",
sum(active_roster.adj_health * player_stats.Blkd) as "Blkd_HOME",
sum(active_roster.adj_health * player_stats."Dist") as "Dist_HOME",
sum(active_roster.adj_health * player_stats."2P_FGA%") as "2P_FGA%_HOME",
sum(active_roster.adj_health * player_stats."0-3ft_FGA%") as "0-3ft_FGA%_HOME",
sum(active_roster.adj_health * player_stats."3-10_FGA%") as "3-10_FGA%_HOME",
sum(active_roster.adj_health * player_stats."10-16ft_FGA%") as "10-16ft_FGA%_HOME",
sum(active_roster.adj_health * player_stats."16-3Pft_FGA%") as "16-3Pft_FGA%_HOME",
sum(active_roster.adj_health * player_stats."3P_FGA%") as "3P_FGA%_HOME",
sum(active_roster.adj_health * player_stats."2P_FG%") as "2P_FG%_HOME",
sum(active_roster.adj_health * player_stats."0-3_FG%") as "0-3_FG%_HOME",
sum(active_roster.adj_health * player_stats."3-10_FG%") as "3-10_FG%_HOME",
sum(active_roster.adj_health * player_stats."10-16_FG%") as "10-16_FG%_HOME",
sum(active_roster.adj_health * player_stats."16-3P_FG%") as "16-3P_FG%_HOME",
sum(active_roster.adj_health * player_stats."3P_FG%") as "3P_FG%_HOME",
sum(active_roster.adj_health * player_stats."2P_FG_AST%") as "2P_FG_AST%_HOME",
sum(active_roster.adj_health * player_stats."3P_FG_AST%") as "3P_FG_AST%_HOME",
sum(active_roster.adj_health * player_stats."%FGA_DUNK") as "%FGA_DUNK_HOME",
sum(active_roster.adj_health * player_stats."#_DUNK") as "#_DUNK_HOME",
sum(active_roster.adj_health * player_stats."%3PA") as "%3PA_HOME",
sum(active_roster.adj_health * player_stats."Att_Heave") as "Att_Heave_HOME",
sum(active_roster.adj_health * player_stats."#_Heave") as "#_Heave_HOME",
schedule.winner as winner
    from (select PLAYER_ID, GAME_DATE, TEAM, ACTIVE,
                 case when PLAYER_ID = :player_id and GAME_DATE = :game_date 
                     then :health 
                     else HEALTH end as adj_health from NBA.ACTIVE_ROSTER) active_roster, nba.schedule, nba.player_stats, nba.team_stats
where active_roster.team = home and active_roster.game_date = schedule.game_date and active_roster.player_id = player_stats.player_id
 and schedule.home = team_stats.team and team_stats.season = :season and PLAYER_STATS.SEASON = :season
 and SCHEDULE.GAME_DATE = :game_date
 group by schedule.game_date, schedule.home, schedule.away, schedule.winner) t1
inner join (select schedule.game_date as game_date,
    schedule.home as home,
    schedule.away as away,
    avg(team_stats."W/L%") as "W/L%_AWAY",
    avg(team_stats.MOV) as "MOV_AWAY",
    avg(team_stats.ORTG) as "ORTG_AWAY",
    avg(team_stats.DRTG) as "DRTG_AWAY",
    avg(team_stats.NRTG) as "NRTG_AWAY",
    avg(team_stats."MOV/A") as "MOV/A_AWAY",
    avg(team_stats."ORtg/A") as "ORtg/A_AWAY",
    avg(team_stats."DRtg/A") as "DRtg/A_AWAY",
    avg(team_stats."NRtg/A") as "NRtg/A_AWAY",
sum(active_roster.adj_health * player_stats.eFG) as "eFG_AWAY",
sum(active_roster.adj_health * player_stats.TS) as "TS_AWAY",
sum(active_roster.adj_health * player_stats.FTr) as "FTr_AWAY",
sum(active_roster.adj_health * player_stats."3PAr") as "3PAr_AWAY",
sum(active_roster.adj_health * player_stats."FG+") as "FG+_AWAY",
sum(active_roster.adj_health * player_stats."2P+") as "2P+_AWAY",
sum(active_roster.adj_health * player_stats."3P+") as "3P+_AWAY",
sum(active_roster.adj_health * player_stats."eFG+") as "eFG+_AWAY",
sum(active_roster.adj_health * player_stats."FT+") as "FT+_AWAY",
sum(active_roster.adj_health * player_stats."TS+") as "TS+_AWAY",
sum(active_roster.adj_health * player_stats."FTr+") as "FTr+_AWAY",
sum(active_roster.adj_health * player_stats."3PAr+") as "3PAr+_AWAY",
sum(active_roster.adj_health * player_stats.FG_Add) as "FG_Add_AWAY",
sum(active_roster.adj_health * player_stats.TS_Add) as "TS_Add_AWAY",
sum(active_roster.adj_health * player_stats.PER) as "PER_AWAY",
sum(active_roster.adj_health * player_stats."TS%") as "TS%_AWAY",
sum(active_roster.adj_health * player_stats."ORB%") as "ORB%_AWAY",
sum(active_roster.adj_health * player_stats."DRB%") as "DRB%_AWAY",
sum(active_roster.adj_health * player_stats."TRB%") as "TRB%_AWAY",
sum(active_roster.adj_health * player_stats."AST%") as "AST%_AWAY",
sum(active_roster.adj_health * player_stats."STL%") as "STL%_AWAY",
sum(active_roster.adj_health * player_stats."BLK%") as "BLK%_AWAY",
sum(active_roster.adj_health * player_stats."TOV%") as "TOV%_AWAY",
sum(active_roster.adj_health * player_stats."USG%") as "USG%_AWAY",
sum(active_roster.adj_health * player_stats.OWS) as "OWS_AWAY",
sum(active_roster.adj_health * player_stats.DWS) as "DWS_AWAY",
sum(active_roster.adj_health * player_stats.WS) as "WS_AWAY",
sum(active_roster.adj_health * player_stats."WS/48") as "WS/48_AWAY",
sum(active_roster.adj_health * player_stats.OBPM) as "OBPM_AWAY",
sum(active_roster.adj_health * player_stats.DBPM) as "DBPM_AWAY",
sum(active_roster.adj_health * player_stats.BPM) as "BPM_AWAY",
sum(active_roster.adj_health * player_stats.VORP) as "VORP_AWAY",
sum(active_roster.adj_health * player_stats.FG) as "FG_AWAY",
sum(active_roster.adj_health * player_stats.FGA) as "FGA_AWAY",
sum(active_roster.adj_health * player_stats."FG%") as "FG%_AWAY",
sum(active_roster.adj_health * player_stats."3P") as "3P_AWAY",
sum(active_roster.adj_health * player_stats."3PA") as "3PA_AWAY",
sum(active_roster.adj_health * player_stats."3P%") as "3P%_AWAY",
sum(active_roster.adj_health * player_stats."2P") as "2P_AWAY",
sum(active_roster.adj_health * player_stats."2PA") as "2PA_AWAY",
sum(active_roster.adj_health * player_stats."2P%") as "2P%_AWAY",
sum(active_roster.adj_health * player_stats."eFG%") as "eFG%_AWAY",
sum(active_roster.adj_health * player_stats."FT") as "FT_AWAY",
sum(active_roster.adj_health * player_stats."FTA") as "FTA_AWAY",
sum(active_roster.adj_health * player_stats."FT%") as "FT%_AWAY",
sum(active_roster.adj_health * player_stats."ORB") as "ORB_AWAY",
sum(active_roster.adj_health * player_stats."DRB") as "DRB_AWAY",
sum(active_roster.adj_health * player_stats."TRB") as "TRB_AWAY",
sum(active_roster.adj_health * player_stats."AST") as "AST_AWAY",
sum(active_roster.adj_health * player_stats."STL") as "STL_AWAY",
sum(active_roster.adj_health * player_stats."BLK") as "BLK_AWAY",
sum(active_roster.adj_health * player_stats."TOV") as "TOV_AWAY",
sum(active_roster.adj_health * player_stats."PF") as "PF_AWAY",
sum(active_roster.adj_health * player_stats."PTS") as "PTS_AWAY",
sum(active_roster.adj_health * player_stats."PE_PG%") as "PE_PG%_AWAY",
sum(active_roster.adj_health * player_stats."PE_SG%") as "PE_SG%_AWAY",
sum(active_roster.adj_health * player_stats."PE_SF%") as "PE_SF%_AWAY",
sum(active_roster.adj_health * player_stats."PE_PF%") as "PE_PF%_AWAY",
sum(active_roster.adj_health * player_stats."PE_C%") as "PE_C%_AWAY",
sum(active_roster.adj_health * player_stats."+/-_OnCourt") as "+/-_OnCourt_AWAY",
sum(active_roster.adj_health * player_stats."+/-_On-Off") as "+/-_On-Off_AWAY",
sum(active_roster.adj_health * player_stats.TO_BadPass) as "TO_BadPass_AWAY",
sum(active_roster.adj_health * player_stats.TO_LostBall) as "TO_LostBall_AWAY",
sum(active_roster.adj_health * player_stats.Shoot_Fl_Com) as "Shoot_Fl_Com_AWAY",
sum(active_roster.adj_health * player_stats."Off._Fl_Com") as "Off._Fl_Com_AWAY",
sum(active_roster.adj_health * player_stats.Shoot_Fl_Drn) as "Shoot_Fl_Drn_AWAY",
sum(active_roster.adj_health * player_stats."Off._Fl_Drn") as "Off._Fl_Drn_AWAY",
sum(active_roster.adj_health * player_stats."PGA") as "PGA_AWAY",
sum(active_roster.adj_health * player_stats.And1) as "And1_AWAY",
sum(active_roster.adj_health * player_stats.Blkd) as "Blkd_AWAY",
sum(active_roster.adj_health * player_stats."Dist") as "Dist_AWAY",
sum(active_roster.adj_health * player_stats."2P_FGA%") as "2P_FGA%_AWAY",
sum(active_roster.adj_health * player_stats."0-3ft_FGA%") as "0-3ft_FGA%_AWAY",
sum(active_roster.adj_health * player_stats."3-10_FGA%") as "3-10_FGA%_AWAY",
sum(active_roster.adj_health * player_stats."10-16ft_FGA%") as "10-16ft_FGA%_AWAY",
sum(active_roster.adj_health * player_stats."16-3Pft_FGA%") as "16-3Pft_FGA%_AWAY",
sum(active_roster.adj_health * player_stats."3P_FGA%") as "3P_FGA%_AWAY",
sum(active_roster.adj_health * player_stats."2P_FG%") as "2P_FG%_AWAY",
sum(active_roster.adj_health * player_stats."0-3_FG%") as "0-3_FG%_AWAY",
sum(active_roster.adj_health * player_stats."3-10_FG%") as "3-10_FG%_AWAY",
sum(active_roster.adj_health * player_stats."10-16_FG%") as "10-16_FG%_AWAY",
sum(active_roster.adj_health * player_stats."16-3P_FG%") as "16-3P_FG%_AWAY",
sum(active_roster.adj_health * player_stats."3P_FG%") as "3P_FG%_AWAY",
sum(active_roster.adj_health * player_stats."2P_FG_AST%") as "2P_FG_AST%_AWAY",
sum(active_roster.adj_health * player_stats."3P_FG_AST%") as "3P_FG_AST%_AWAY",
sum(active_roster.adj_health * player_stats."%FGA_DUNK") as "%FGA_DUNK_AWAY",
sum(active_roster.adj_health * player_stats."#_DUNK") as "#_DUNK_AWAY",
sum(active_roster.adj_health * player_stats."%3PA") as "%3PA_AWAY",
sum(active_roster.adj_health * player_stats."Att_Heave") as "Att_Heave_AWAY",
sum(active_roster.adj_health * player_stats."#_Heave") as "#_Heave_AWAY"
    from (select PLAYER_ID, GAME_DATE, TEAM, ACTIVE,
                 case when PLAYER_ID = :player_id and GAME_DATE = :game_date
                     then :health
                     else HEALTH end as adj_health from NBA.ACTIVE_ROSTER) active_roster, nba.schedule, nba.player_stats, nba.team_stats
where active_roster.team = away and active_roster.game_date = schedule.game_date and active_roster.player_id = player_stats.player_id
    and schedule.away = team_stats.team and team_stats.season = :season and PLAYER_STATS.SEASON = :season
    and SCHEDULE.GAME_DATE = :game_date
 group by schedule.game_date, schedule.home, schedule.away) t2
    on t1.game_date = t2.game_date and t1.home=t2.home and t1.away=t2.away where t1.home = :team or t1.away = :team;

