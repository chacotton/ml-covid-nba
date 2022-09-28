from abc import ABC, abstractmethod
import mlflow
import pandas as pd


class NBAModel(ABC):
    """
    Abstract Base Class Representing NBA Models using MLFlow functions

    MLFlow models work by loading serialized prediction function then passing inputs through python function
    Class also contains result writing utilities
    """
    def __init__(self, model_file, *args, **kwargs):
        self.model = self._load_model(model_file)

    @staticmethod
    def _load_model(model_file: str):
        """Load serialized model based on file reference"""
        return mlflow.pyfunc.load_model(model_file)

    def _test_model(self):
        """Run model on dummy data to produce output"""
        raise NotImplementedError

    @abstractmethod
    def predict(self, x: pd.DataFrame):
        raise NotImplementedError

    # TODO: Define Common Functions
