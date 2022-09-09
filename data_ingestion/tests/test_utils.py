import pandas as pd
from data_ingestion.utils import _get_engine, read_table, write_db

sql_file = "queries/test.sql"
sql_command = "SELECT * FROM NBA.SCHEDULE"
sql_command_bind = "SELECT * FROM NBA.SCHEDULE WHERE HOME = :team"


class TestUtils:
    def test_get_engine(self):
        engine = _get_engine()
        with engine.connect() as conn:
            assert conn

    def test_read_table(self):
        assert isinstance(read_table(sql_file, team='Dallas Mavericks'), pd.DataFrame)
        assert isinstance(read_table(sql_command), pd.DataFrame)
        assert isinstance(read_table(sql_command_bind, team='Dallas Mavericks'), pd.DataFrame)

    def test_write_db(self):
        assert write_db(sql_file, team='Dallas Mavericks')
        assert write_db(sql_command)
        assert write_db(sql_command_bind, team='Dallas Mavericks')