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
    df.to_csv('NBA_Injury_Data.csv', index = False)