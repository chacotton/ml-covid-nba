from abc import ABC, abstractmethod
import mlflow
import pandas as pd
from contextlib import redirect_stdout
from datetime import date, timedelta
from modeling.utils import read_table
import os


class NBAModel(ABC):
    """
    Abstract Base Class Representing NBA Models using MLFlow functions

    MLFlow models work by loading serialized prediction function then passing inputs through python function
    Class also contains result writing utilities
    """
    monitoring_query = None

    def __init__(self, model_file, *args, **kwargs):
        self.model = self._load_model(model_file)

    @staticmethod
    def _load_model(model_file: str):
        """Load serialized model based on file reference"""
        with open(os.devnull, 'w') as devnull:
            with redirect_stdout(devnull):
                model = mlflow.pyfunc.load_model(model_file)
        return model

    @classmethod
    def score_model(cls, start_date: date = None, end_date: date = None, days_range: int = 7):
        """
        Runs a performance analysis query based on query file defined in the model subclass
        accepts a start and end date (non-inclusive), a start date and range, an end date and range,
        if none are filled then will use 7 days prior to today's date

        subclass query file must only have 2 bind variables, (start_date, end_date) of type datetime.date

        :param start_date: datetime object specifying start date
        :param end_date: datetime object specifying start date
        :param days_range: integer days range if start or end not specified, default is 7 days
        :return: pd.DataFrame of score metric, output is defined by query file itself
        """
        if start_date is None and end_date is None:
            end_date = date.today()
            start_date = end_date - timedelta(days=days_range)
        elif end_date is not None:
            start_date = end_date - timedelta(days=days_range)
        else:
            end_date = start_date + timedelta(days=days_range)
        return read_table(cls.monitoring_query, start_date=start_date, end_date=end_date)

    def _test_model(self):
        """Run model on dummy data to produce output"""
        raise NotImplementedError

    @abstractmethod
    def predict(self, x: pd.DataFrame):
        raise NotImplementedError

