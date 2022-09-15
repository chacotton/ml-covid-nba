import pandas as pd
import pytest
from data_ingestion.injury_labeller.injuryScore import InjuryScore
from basketball_reference_scraper.box_scores import get_box_scores


class TestInjuryScore:

    def test_calcDist(self):
        ic = InjuryScore("Joel Embiid", 2021)
        assert ic.calc_dist('NOP', 'GSW') == 1919.9550708693628

    def test_getScore(self):
        ic = InjuryScore("Joel Embiid", 2021)
        ret_df = ic.getInjuryScore()
        assert isinstance(ret_df, pd.DataFrame)

    def test_pie_health_score(self):
        ic = InjuryScore("Joel Embiid", 2021)
        ret_df = ic.pie_health_score()
        assert isinstance(ret_df, pd.DataFrame)
        assert not ret_df.empty

    def test_isValid(self):
        ic = InjuryScore("Joel Embiid", 2021)
        ret_df = ic.getInjuryScore()
        df2 = ret_df[(ret_df['Injury and Fatigue Score'] < 0) | (ret_df['Injury and Fatigue Score'] > 1.0)]
        assert df2.empty
        assert df2.shape[1] == 3

    def test_pie_score(self):
        box = get_box_scores('2021-12-17', 'MIA', 'ORL')['MIA']
        score = InjuryScore.pie_score(box, box.player_id[0])
        assert 0 <= score < 1

    def test_fake_name(self):
        with pytest.raises(ValueError):
            InjuryScore('Fake Name', 2021)

    def test_fake_id(self):
        with pytest.raises(ValueError):
            InjuryScore('fakename', 2021)


