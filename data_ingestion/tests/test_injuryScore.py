import pandas as pd
from data_ingestion.injury_labeller.injuryScore import InjuryScore


class TestInjuryScore:
    def test_regression_calc(self):
        assert InjuryScore.regressionCalc('player is (out for season)') == -1
        assert InjuryScore.regressionCalc('I am sore') == -.1
        assert InjuryScore.regressionCalc('Surgery') == -.1
        assert InjuryScore.regressionCalc('an injury') == -.1

    def test_calcDist(self):
        ic = InjuryScore("Joel Embiid", 2021)
        assert ic.calc_dist('NOP', 'GSW') == 1919.9550708693628

    def test_day_diff(self):
        pass

    def test_getScore(self):
        ic = InjuryScore("Joel Embiid", 2021)
        ret_df = ic.getInjuryScore()
        assert isinstance(ret_df, pd.DataFrame)

    def test_isValid(self):
        ic = InjuryScore("Joel Embiid", 2021)
        ret_df = ic.getInjuryScore()
        df2 = ret_df[(ret_df['Injury and Fatigue Score'] < 0) | (ret_df['Injury and Fatigue Score'] > 1.0)]
        assert df2.empty
        assert df2.shape[1] == 3

    def test_nameToDf(self):
        ic = InjuryScore("Joel Embiid", 2021)
        assert isinstance(ic.playerToDf('Joel Embiid', 2019),pd.DataFrame)

    def test_idToDf(self):
        ic = InjuryScore("Joel Embiid", 2021)
        assert isinstance(ic.idToDf('horfoal01', 2019),pd.DataFrame)

    def test_id_to_name(self):
        pass

    def test_regressors(self):
        pass

