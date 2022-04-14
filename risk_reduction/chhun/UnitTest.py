import unittest
import cx_Oracle
from sqlalchemy import create_engine
import config
import pandas as pd
from data import chance_of_victory


TABLENAME = 'pytabchhun'
cx_Oracle.init_oracle_client(lib_dir="instantclient_19_8")
engine = create_engine('oracle+cx_oracle://{}:{}@{}'.format(config.username, config.password, config.dsn))


class MyTestCase(unittest.TestCase):


    def test_data_insertion(self):
        df = chance_of_victory.WinDataset(optimize=True).get_dataset()
        df.to_sql(TABLENAME, engine, if_exists='replace', index=False)
        output = pd.read_sql("""Select * from pytabchhun""", engine)
        self.assertEqual(True, df.equals(output))

    def test_schema(self):
        df = chance_of_victory.WinDataset(optimize=True).get_dataset()
        list1 = list(df.columns)
        columns = """Select column_name FROM all_tab_columns
        where table_name = 'PYTABCHHUN' and owner = 'NBACOVID'"""
        df_schema = pd.read_sql(columns, engine)
        columns = []
        for c in df_schema.itertuples():
            columns.append(c.column_name)
        self.assertListEqual(sorted(list1), sorted(columns))

    def test_exist_table(self):
        query_statement = "SELECT owner, TABLE_name FROM all_tables where owner = 'NBACOVID' and table_name='PYTABCHHUN'"
        result = engine.execute(query_statement)
        self.assertIsNotNone(result.first())

if __name__ == '__main__':
    unittest.main()
