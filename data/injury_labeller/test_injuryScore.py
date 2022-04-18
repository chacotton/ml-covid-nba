import pandas as pd
from injuryScore import injuryScore



def test_calcDist():
    
    ic = injuryScore("joel_embiid_2020_2021.csv", "Joel Embiid")
    assert ic.calcDist('NOP', 'GSW') == 1919.9550708693628

def test_getScore():
    ic = injuryScore("joel_embiid_2020_2021.csv", "Joel Embiid")
    ret_df = ic.getInjuryScore()
    assert isinstance(ic.getInjuryScore(),pd.DataFrame) is True

def test_isValid():
    ic = injuryScore("joel_embiid_2020_2021.csv", "Joel Embiid")
    ret_df = ic.getInjuryScore()
    df2 = ret_df[(ret_df['Injury and Fatigue Score'] < 0) | (ret_df['Injury and Fatigue Score'] > 1.0)]
    assert df2.empty is True

def test_validColumns():
    ic = injuryScore("joel_embiid_2020_2021.csv", "Joel Embiid")
    ret_df = ic.getInjuryScore()
    df2 = ret_df[(ret_df['Injury and Fatigue Score'] < 0) | (ret_df['Injury and Fatigue Score'] > 1.0)]
    assert df2.shape[1] == 4
def test_nameToDf():
    ic = injuryScore("joel_embiid_2020_2021.csv", "Joel Embiid")
    assert isinstance(ic.playerToDf('Joel Embiid', 2019),pd.DataFrame) is True

def test_idToDf():
    ic = injuryScore("joel_embiid_2020_2021.csv", "Joel Embiid")
    assert isinstance(ic.idToDf('horfoal01', 2019),pd.DataFrame) is True
