MERGE INTO NBA.TEAM_STATS_DUMMY dest
USING ( SELECT
:TEAM TEAM, :CONF CONF, :DIV DIV, :W W, :L L, :WSLP "W/L%", :MOV MOV, :ORTG ORTG, :DRTG DRTG, :NRTG NRTG, :MOVSA "MOV/A",
:ORTGSA "ORtg/A", :DRTGSA "DRtg/A", :NRTGSA "NRtg/A", :SEASON SEASON
FROM dual) src
ON (dest.TEAM = src.TEAM and dest.SEASON = src.SEASON)
WHEN MATCHED THEN
    UPDATE SET W = src.W, L = src.L, "W/L%" = src."W/L%", MOV = src.MOV, ORTG = src.ORTG, DRTG = src.DRTG, NRTG = src.NRTG,
               "MOV/A" = src."MOV/A", "ORtg/A" = src."ORtg/A", "DRtg/A" = src."DRtg/A", "NRtg/A" = src."DRtg/A"
WHEN NOT MATCHED THEN
    INSERT(TEAM, CONF, DIV, W, L, "W/L%", MOV, ORTG, DRTG, NRTG, "MOV/A", "ORtg/A", "DRtg/A", "NRtg/A", SEASON)
    VALUES (src.TEAM, src.CONF, src.DIV, src.W, src.L, src."W/L%", src.MOV, src.ORTG, src.DRTG, src.NRTG, src."MOV/A",
            src."ORtg/A", src."DRtg/A", src."NRtg/A", src.SEASON);
