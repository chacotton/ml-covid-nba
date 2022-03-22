"""Module to scrape NBA data"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path

BASKETBALL_REF = "https://www.basketball-reference.com/"
NBA_INJURY_REPORT = "https://www.prosportstransactions.com/basketball/Search/SearchResults.php?" \
                    "Player=&Team=&BeginDate=2020-03-01&EndDate=2022-02-18&ILChkBx=yes&Submit=Search&start="

MONTHS = ['october', 'november', 'december', 'january', 'february', 'march', 'april']


def covid_data_scraper(save: bool = False) -> pd.DataFrame:
    """
    Scrapes NBA Injury Report
    :param save: bool, default = False, whether to save to csv file
    :return: pd.DataFrame, DataFrame holding scraped data
    """
    df = pd.DataFrame(columns=['Date', 'Team', 'Acquired', 'Relinquished', 'Notes'])
    for index in range(0, 167*25, 25):
        request = requests.get(NBA_INJURY_REPORT + str(index))
        bs_result = BeautifulSoup(request.content, 'html.parser')
        table = bs_result.find('table', class_='datatable')
        for r in table.find_all('tr'):
            columns = r.find_all('td')
            date = columns[0].text.strip()
            team = columns[1].text.strip()
            acquired = columns[2].text.strip()
            relinquished = columns[3].text.strip()
            notes = columns[4].text.strip()
            df = df.append({'Date': date, 'Team': team, 'Acquired': acquired, 'Relinquished': relinquished, 'Notes': notes}, ignore_index=True)
    if save:
        df.to_csv(Path(__file__).parent / 'covid_data/NBA_Injury_Data.csv', index=False)
    return df


def game_data_scraper(save: bool = False) -> pd.DataFrame:
    """
    Scrapes active roster per game in 21-22
    :param save: bool, default = False, whether to save to csv file
    :return: pd.DataFrame, DataFrame holding scraped data
    """
    columns = ['Date', 'Away', 'Away_pts', 'Home', 'Home_pts'] + [f'{site}_player_{i}' for site in ['Away', 'Home'] for i in range(15)]
    df = pd.DataFrame(columns=columns)
    for month in MONTHS:
        request = requests.get(BASKETBALL_REF + f"leagues/NBA_2022_games-{month}.html")
        bs = BeautifulSoup(request.content, 'html.parser')
        table = bs.find(id='schedule')
        try:
            for i, row in enumerate(table.find_all('tr')):
                df_row = []
                if i == 0:
                    continue
                for j, col in enumerate(row.find_all('a')):
                    if j == 3:
                        request = requests.get(BASKETBALL_REF + col['href'])
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
                df.loc[len(df)] = df_row
        except (ValueError, requests.exceptions.RequestException):
            break
    if save:
        df.to_csv(Path(__file__).parent / 'team_data/NBA_games_21-22.csv', index=False)
    return df


if __name__ == '__main__':
    covid_data_scraper()
    game_data_scraper()
