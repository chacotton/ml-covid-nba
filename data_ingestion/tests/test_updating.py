from data_ingestion import update_player_stats, update_team_stats, update_roster
import pytest
from data_ingestion.stat_utils import join_player_stats
from data_ingestion.db_utils import get_engine, read_table
from datetime import date

schedule = "SELECT * FROM NBA.SCHEDULE WHERE GAME_DATE = :day FETCH NEXT 1 ROWS ONLY"


class TestUpdate:
    def test_join_player_stats(self):
        df = join_player_stats('doncilu01', 2021)
        assert df.shape[0] == 1
        df = join_player_stats('doncilu01', 2000)
        assert df.empty
        with pytest.raises(KeyError):
            join_player_stats('doncilu00', 2021)

    def test_update_player_stats(self):
        game = read_table(schedule, day=date(2022, 1, 10))
        no_game = read_table(schedule, day=date(2022, 7, 1))
        with get_engine().connect() as conn:
            assert update_player_stats(game, conn)
            assert not update_player_stats(no_game, conn)

    def test_update_team_stats(self):
        game = read_table(schedule, day=date(2022, 1, 10))
        no_game = read_table(schedule, day=date(2022, 7, 1))
        with get_engine().connect() as conn:
            assert update_team_stats(game, conn)
            assert not update_team_stats(no_game, conn)

    #def test_update_active_roster(self):
    #    game = read_table(schedule, day=date(2022, 1, 10))
    #    no_game = read_table(schedule, day=date(2022, 7, 1))
    #    with get_engine().connect() as conn:
    #        assert update_roster(game, conn)
    #        assert not update_roster(no_game, conn)