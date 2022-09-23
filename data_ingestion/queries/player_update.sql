MERGE INTO NBA.DUMMY_PLAYER_STATS dest
USING ( SELECT
:PLAYER_ID PLAYER_ID, :PLAYER PLAYER, :POS POS, :AGE AGE, :TEAM TEAM, :G G, :MP MP, :FG FG, :TP "2P", :HP "3P",
:EFG EFG, :FT FT, :TS TS, :FTR FTR, :HPAR "3PAr", :FGL "FG+", :TPL "2P+", :HPL "3P+", :EFGL "eFG+", :FTL "FT+",
:TSL "TS+", :FTRL "FTr+", :HPARL "3PAr+", :FG_ADD FG_ADD, :TS_ADD TS_ADD, :PER PER, :TSP "TS%", :ORBP "ORB%",
:DRBP "DRB%", :TRBP "TRB%", :ASTP "AST%", :STLP "STL%", :BLKP "BLK%", :TOVP "TOV%", :USGP "USG%", :OWS OWS,
:DWS DWS, :WS WS, :WSS48 "WS/48", :OBPM OBPM, :DBPM DBPM, :BPM BPM, :VORP VORP, :FGA FGA, :FGP "FG%", :HPA "3PA",
:HPP "3P%", :TPA "2PA", :TPP "2P%", :EFGP "eFG%", :FTA FTA, :FTP "FT%", :ORB ORB, :DRB DRB, :TRB TRB,
:AST AST, :STL STL, :BLK BLK, :TOV TOV, :PF PF, :PTS PTS, :PE_PGP "PE_PG%", :PE_SGP "PE_SG%", :PE_SFP "PE_SF%",
:PE_PFP "PE_PF%", :PE_CP "PE_C%", :LSM_ONCOURT "+/-_OnCourt", :LSM_ONMOFF "+/-_On-Off", :TO_BADPASS TO_BADPASS,
:TO_LOSTBALL TO_LOSTBALL, :SHOOT_FL_COM SHOOT_FL_COM, :OFFD_FL_COM "Off._Fl_Com", :SHOOT_FL_DRN SHOOT_FL_DRN, :OFFD_FL_DRN "Off._Fl_Drn",
:PGA PGA, :ANDO AND1, :BLKD BLKD, :DIST "Dist", :TP_FGAP "2P_FGA%", :ZMHFT_FGAP "0-3ft_FGA%", :HMOZ_FGAP "3-10_FGA%",
:OZMO6FT_FGAP "10-16ft_FGA%", :O6MHPFT_FGAP "16-3Pft_FGA%", :HP_FGAP "3P_FGA%", :TP_FGP "2P_FG%", :ZMH_FGP "0-3_FG%",
:HMOZ_FGP "3-10_FG%", :OZMO6_FGP "10-16_FG%", :O6MHP_FGP "16-3P_FG%", :HP_FGP "3P_FG%", :TP_FG_ASTP "2P_FG_AST%",
:HP_FG_ASTP "3P_FG_AST%", :PFGA_DUNK "%FGA_DUNK", :N_DUNK "#_DUNK", :PHPA "%3PA", :ATT_HEAVE "Att_Heave", :N_HEAVE "#_Heave", :SEASON SEASON, :PIE PIE
FROM dual) src
ON (dest.PLAYER_ID = src.PLAYER_ID and dest.SEASON = src.SEASON)
WHEN MATCHED THEN
    UPDATE SET G = src.G, MP = src.MP, FG = src.FG, "2P" = src."2P", "3P" = src."3P", EFG = src.EFG,
               FT = src.FT, TS = src.TS, FTR = src.FTR, "3PAr" = src."3PAr", "FG+" = src."FG+", "2P+" = src."2P+", "3P+" = src."3P+",
               "eFG+" = src."eFG+", "FT+" = src."FT+", "TS+" = src."TS+", "FTr+" = src."FTr+", "3PAr+" = src."3PAr+", FG_ADD = src.FG_ADD,
               TS_ADD = src.TS_ADD, PER = src.PER, "TS%" = src."TS%", "ORB%" = src."ORB%", "DRB%" = src."DRB%", "TRB%" = src."TRB%",
               "AST%" = src."AST%", "STL%" = src."STL%", "BLK%" = src."BLK%", "TOV%" = src."TOV%", "USG%" = src."USG%", OWS = src.OWS,
               DWS = src.DWS, WS = src.WS, "WS/48" = src."WS/48", OBPM = src.OBPM, DBPM = src.DBPM, BPM = src.BPM, VORP = src.VORP,
               FGA = src.FGA, "FG%" = src."FG%", "3PA" = src."3PA", "3P%" = src."3P%", "2PA" = src."2PA", "2P%" = src."2P%",
               "eFG%" = src."eFG%", FTA = src.FTA, "FT%" = src."FT%", ORB = src.ORB, DRB = src.DRB, TRB = src.TRB,
               AST = src.AST, STL = src.STL, BLK = src.BLK, TOV = src.TOV, PF = src.PF, PTS = src.PTS, "PE_PG%" = src."PE_PG%",
               "PE_SG%" = src."PE_SG%", "PE_SF%" = src."PE_SF%", "PE_PF%" = src."PE_PF%", "PE_C%" = src."PE_C%", "+/-_OnCourt" = src."+/-_OnCourt",
               "+/-_On-Off" = src."+/-_On-Off", TO_BADPASS = src.TO_BADPASS, TO_LOSTBALL = src.TO_LOSTBALL, SHOOT_FL_COM = src.SHOOT_FL_COM,
               "Off._Fl_Com" = src."Off._Fl_Com", SHOOT_FL_DRN = src.SHOOT_FL_DRN, "Off._Fl_Drn" = src."Off._Fl_Drn", PGA = src.PGA,
               AND1 = src.AND1, BLKD = src.BLKD, "Dist" = src."Dist", "2P_FGA%" = src."2P_FGA%", "0-3ft_FGA%" = src."0-3ft_FGA%",
               "3-10_FGA%" = src."3-10_FGA%", "10-16ft_FGA%" = src."10-16ft_FGA%", "16-3Pft_FGA%" = src."16-3Pft_FGA%", "3P_FGA%" = src."3P_FGA%",
               "2P_FG%" = src."2P_FG%", "0-3_FG%" = src."0-3_FG%", "3-10_FG%" = src."3-10_FG%", "10-16_FG%" = src."10-16_FG%", "16-3P_FG%" = src."16-3P_FG%",
               "3P_FG%" = src."3P_FG%", "2P_FG_AST%" = src."2P_FG_AST%", "3P_FG_AST%" = src."3P_FG_AST%", "%FGA_DUNK" = src."%FGA_DUNK", "#_DUNK" = src."#_DUNK",
               "%3PA" = src."%3PA", "Att_Heave" = src."Att_Heave", "#_Heave" = src."#_Heave"
WHEN NOT MATCHED THEN
    INSERT (PLAYER_ID, PLAYER, POS, AGE, TEAM, G, MP, FG, "2P", "3P", EFG, FT, TS, FTR, "3PAr", "FG+", "2P+", "3P+",
            "eFG+", "FT+", "TS+", "FTr+", "3PAr+", FG_ADD, TS_ADD, PER, "TS%", "ORB%", "DRB%", "TRB%",
            "AST%", "STL%", "BLK%", "TOV%", "USG%", OWS, DWS, WS, "WS/48", OBPM, DBPM, BPM, VORP, FGA, "FG%",
            "3PA", "3P%", "2PA", "2P%", "eFG%", FTA, "FT%", ORB, DRB, TRB, AST, STL, BLK, TOV, PF, PTS, "PE_PG%", "PE_SG%",
            "PE_SF%", "PE_PF%", "PE_C%", "+/-_OnCourt", "+/-_On-Off", TO_BADPASS, TO_LOSTBALL, SHOOT_FL_COM, "Off._Fl_Com",
            SHOOT_FL_DRN, "Off._Fl_Drn", PGA, AND1, BLKD, "Dist", "2P_FGA%", "0-3ft_FGA%", "3-10_FGA%", "10-16ft_FGA%",
            "16-3Pft_FGA%", "3P_FGA%", "2P_FG%", "0-3_FG%", "3-10_FG%", "10-16_FG%", "16-3P_FG%", "3P_FG%", "2P_FG_AST%",
            "3P_FG_AST%", "%FGA_DUNK", "#_DUNK", "%3PA", "Att_Heave", "#_Heave", SEASON, PIE)
    VALUES (src.PLAYER_ID, src.PLAYER, src.POS, src.AGE, src.TEAM, src.G, src.MP, src.FG, src."2P", src."3P", src.EFG, src.FT,
            src.TS, src.FTR, src."3PAr", src."FG+", src."2P+", src."3P+",
            src."eFG+", src."FT+", src."TS+", src."FTr+", src."3PAr+", src.FG_ADD, src.TS_ADD, src.PER, src."TS%", src."ORB%", src."DRB%", src."TRB%",
            src."AST%", src."STL%", src."BLK%", src."TOV%", src."USG%", src.OWS, src.DWS, src.WS, src."WS/48", src.OBPM, src.DBPM, src.BPM, src.VORP, src.FGA, src."FG%",
            src."3PA", src."3P%", src."2PA", src."2P%", src."eFG%", src.FTA, src."FT%", src.ORB, src.DRB, src.TRB, src.AST,
            src.STL, src.BLK, src.TOV, src.PF, src.PTS, src."PE_PG%", src."PE_SG%",
            src."PE_SF%", src."PE_PF%", src."PE_C%", src."+/-_OnCourt", src."+/-_On-Off", src.TO_BADPASS, src.TO_LOSTBALL,
            src.SHOOT_FL_COM, src."Off._Fl_Com",
            src.SHOOT_FL_DRN, src."Off._Fl_Drn", src.PGA, src.AND1, src.BLKD, src."Dist", src."2P_FGA%", src."0-3ft_FGA%", src."3-10_FGA%", src."10-16ft_FGA%",
            src."16-3Pft_FGA%", src."3P_FGA%", src."2P_FG%", src."0-3_FG%", src."3-10_FG%", src."10-16_FG%", src."16-3P_FG%", src."3P_FG%", src."2P_FG_AST%",
            src."3P_FG_AST%", src."%FGA_DUNK", src."#_DUNK", src."%3PA", src."Att_Heave", src."#_Heave", src.SEASON, src.PIE);


