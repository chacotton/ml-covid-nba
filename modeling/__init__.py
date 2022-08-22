from abc import ABC, abstractmethod


class NBAModel(ABC):
    """
    Abstract Base Class Representing NBA Models using MLFlow functions

    MLFlow models work by loading serialized prediction function then passing inputs through python function
    Class also contains result writing utilities
    """
    def __init__(self, *args, **kwargs):
        self.model = None

    def _load_model(self, model_file: str):
        """Load serialized model based on file reference"""
        raise NotImplementedError

    def _test_model(self):
        """Run model on dummy data to produce output"""
        raise NotImplementedError

    @abstractmethod
    def predict(self, x: dict) -> float:
        raise NotImplementedError

    # TODO: Define Common Functions
