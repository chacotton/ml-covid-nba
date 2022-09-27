from nba_api.stats.endpoints import playergamelogs


def is_active(date, player):
    mdy = date.replace('-', '/').split("/")
    if int(mdy[0]) <= 5:
        currSeason = str(int(mdy[2]) - 1) + '-' + mdy[2][2:]
    else:
        currSeason = mdy[2] + '-' + str(int(mdy[2]) + 1)[2:]
    #print(currSeason)
    c = playergamelogs.PlayerGameLogs(
        season_nullable = currSeason,
        date_from_nullable = mdy[0] + '/' + mdy[1] + '/' + mdy[2],                                                     
        date_to_nullable = mdy[0] + '/' + mdy[1] + '/' + mdy[2]
    ).player_game_logs.get_data_frame()
    #print(c[['PLAYER_NAME', 'MIN']])
    return player in c['PLAYER_NAME'].values

print(is_active("10-25/2021", "Paul Millsap"))