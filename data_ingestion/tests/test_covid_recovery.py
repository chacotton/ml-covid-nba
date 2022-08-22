import pandas as pd
from data_ingestion import covid_recovery


class TestCovidRecovery:
    def test_init(self):
        df = covid_recovery.Covid().get_dataset()
        assert isinstance(df, pd.DataFrame)
        assert df.shape[:2] == (501, 5)     # Checks shape of dataframe

    def test_recovery(self):
        df = covid_recovery.Covid()._covid_dataset()
        assert isinstance(df, pd.DataFrame)
        result = df[df.Deactivated > df.Activated]
        assert result.empty

    def test_create_dataset(self):
        df = covid_recovery.Covid()._create_dataset()
        assert isinstance(df, pd.DataFrame)
