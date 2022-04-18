import pandas as pd
from injuryScore import injuryScore


class TestInjuryScore:
    def test_calcDist(self):
        ic = injuryScore("embiijo01", 2021)
        assert ic.calcDist('NOP', 'GSW') == 1919.9550708693628

    def test_getScore(self):
        ic = injuryScore("embiijo01", 2021)
        ret_df = ic.getInjuryScore()
        assert isinstance(ic.getInjuryScore(),pd.DataFrame)

    def test_isValid(self):
        ic = injuryScore("embiijo01", 2021)
        ret_df = ic.getInjuryScore()
        df2 = ret_df[(ret_df['Injury and Fatigue Score'] < 0) | (ret_df['Injury and Fatigue Score'] > 1.0)]
        assert df2.empty

    def test_validColumns(self):
        ic = injuryScore("embiijo01", 2021)
        ret_df = ic.getInjuryScore()
        df2 = ret_df[(ret_df['Injury and Fatigue Score'] < 0) | (ret_df['Injury and Fatigue Score'] > 1.0)]
        assert df2.shape[1] == 4

    def test_nameToDf(self):
        ic = injuryScore("embiijo01", 2021)
        assert isinstance(ic.playerToDf('Joel Embiid', 2019),pd.DataFrame)

    def test_idToDf(self):
        ic = injuryScore("embiijo01", 2021)
        assert isinstance(ic.idToDf('horfoal01', 2019),pd.DataFrame)
