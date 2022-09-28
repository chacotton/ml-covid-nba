import pandas as pd
import pytest
import time
from data_ingestion.db_utils import get_engine, read_table, write_db, timeout

sql_file = "test.sql"
sql_command = "SELECT * FROM NBA.SCHEDULE"
sql_command_bind = "SELECT * FROM NBA.SCHEDULE WHERE HOME = :team"


class TestUtils:
    def test_get_engine(self):
        engine = get_engine()
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

    def test_timeout(self):
        with pytest.raises(TimeoutError):
            timeout(3, time.sleep, func_args=(4,))
