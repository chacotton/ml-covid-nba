import requests
from bs4 import BeautifulSoup
import pandas as pd 


def covid_data_scraper():
    index = 0
    df = pd.DataFrame(columns=['Date', 'Team', 'Acquired', 'Relinquished', 'Notes'])
    for i in range(0, 167):
        request = requests.get('https://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate=2020-03-01&EndDate=2022-02-18&ILChkBx=yes&Submit=Search&start=' + str(index))
        bs_result = BeautifulSoup(request.content, 'html.parser')
        table = bs_result.find('table', class_='datatable')
        for r in table.find_all('tr'):
            columns = r.find_all('td')
            date = columns[0].text.strip()
            team = columns[1].text.strip()
            acquired = columns[2].text.strip()
            relinquished = columns[3].text.strip()
            notes = columns[4].text.strip()
            df = df.append({'Date': date, 'Team': team, 'Acquired': acquired, 'Relinquished': relinquished, 'Notes': notes }, ignore_index=True)
        index += 25
    df.to_csv('covid_data/NBA_Injury_Data.csv', index = False)


def game_data_scraper():
    columns = ['Date', 'Away', 'Away_pts', 'Home', 'Home_pts'] + [f'Away_player_{i}' for i in range(15)] + [f'Home_player_{i}' for i in range(15)]
    df = pd.DataFrame(columns=columns)
    for month in ['october','november','december','january','february','march']:
        request = requests.get(f"https://www.basketball-reference.com/leagues/NBA_2022_games-{month}.html")
        bs = BeautifulSoup(request.content, 'html.parser')
        table = bs.find(id='schedule')
        for i, row in enumerate(table.find_all('tr')):
            df_row = []
            if i == 0:
                continue
            for j, col in enumerate(row.find_all('a')):
                if j == 3:
                    try:
                        request = requests.get("https://www.basketball-reference.com/" + col['href'])
                    except:
                        df.to_csv('/team_data/NBA_games_21-22.csv',index=False)
                        return df
                    box_scores = BeautifulSoup(request.content, 'html.parser')
                    for team in list(filter(lambda x: len(x.text) == 3, box_scores.find_all('strong'))):
                        players = box_scores.find_all('table', id=f'box-{team.text}-game-basic')[0].find_all('th', {'data-stat': 'player'})
                        players = [p.text + '/' + p['data-append-csv'] for p in players if p.get('data-append-csv', 0) != 0]
                        players = [players[i] if i < len(players) else '' for i in range(15)]
                        df_row += players
                else:
                    df_row.append(col.text)
                if j == 1:
                    df_row.append(row.find('td', {'data-stat': 'visitor_pts'}).text)
                elif j == 2:
                    df_row.append(row.find('td', {'data-stat': 'home_pts'}).text)
            try:
                df.loc[len(df)] = df_row
            except ValueError:
                df.to_csv('team_data/NBA_games_21-22.csv', index=False)
                return df
    df.to_csv('/team_data/NBA_games_21-22.csv', index=False)
    return df




if __name__ == '__main__':
    #covid_data_scraper()
    df = game_data_scraper()
    pass
