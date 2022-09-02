import oracledb
from pathlib import Path

wallet_dir = Path(__file__).resolve().parent / Path("wallet")

db_args = {
    "user": "nba",
    "password": "SeniorDesign22",
    "dsn": "nba_low",
    "config_dir": wallet_dir,
    "wallet_location": wallet_dir,
    "wallet_password": "password1",
}

sql_get = "SELECT game_date, home, away FROM nba.schedule ORDER BY game_date"
sql_set = "UPDATE nba.dummy_schedule SET HOME_WIN_PROB = :win, AWAY_WIN_PROB = :lose WHERE game_date = :game and away = :away and home = :home"

if __name__ == '__main__':
    with oracledb.connect(**db_args) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(sql_get)
            row = cur.fetchone()
            set_args = {
                'game': row[0],
                'home': row[1],
                'away': row[2],
                'win': .6,
                'lose': .4,
            }
            cur.execute(sql_set, **set_args)
    print("Success")

