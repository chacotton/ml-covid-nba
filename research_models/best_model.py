import sys
from sqlalchemy import create_engine
from query_templates import *
from collections import namedtuple
from importlib import import_module


class ModelGenerator:
    """Selects Best Model from MLFlow logging"""

    hosts = {
        "darwin": "127.0.0.1:3307",
        "linux": "10.0.0.150",
    }

    metrics = {
        "regression": "r2",
        "classification": "accuracy"
    }

    model = namedtuple('model', 'model params')

    @classmethod
    def list_to_str(cls, ids: list) -> str:
        """
        Takes list of strings and converts to one comma separated string
        :param ids: list of strings
        :return: str
        """

        return ", ".join(["'" + _id + "'" for _id in ids])

    def __init__(self, database="test"):
        """
        Initialization for ModelGenerator
        :param database: name of database to select best model from options are ['test', 'win', 'covid']
        """

        assert database in ['test', 'win', 'covid'], "Valid databases are 'test', 'win', or 'covid'"
        system = sys.platform
        self.db = create_engine(f'mysql+pymysql://admin:NBACovid19!@{self.hosts.get(system, "10.0.0.150")}/{database}_db')
        self.db.connect()
        self._model_id = None
        self.best_model_name = None
        self.model_params = None
        self.meta_data = None

    def _get_best_model_name(self, problem: str = 'regression'):
        """
        Helper function to get best model data
        :param problem: str , must be in ['classification', 'regression']
        :return: None
        """

        result = self.db.execute(BEST.substitute({'type': problem, 'metric': self.metrics[problem]}))
        self.best_model_name, self._model_id = next(result)

    def _get_best_model_params(self) -> dict:
        """
        Helper function to place best model parameters in dictionary
        :return: None
        """

        result = self.db.execute(PARAMS.substitute({'run_id': self._model_id}))
        return {k: v for k, v in result}

    def get_best_model(self, problem: str = 'regression') -> model:
        """
        Function to return initialized best model and parameters for model
        *Currently model instantiation is only supported for Sci-Kit Learn Models (sklearn)
            Models from other libraries will be returned as name only
        :param problem: str, must be 'classification' or 'regression'
        :return: model, namedtuple with attributes model (instantiated model or model name)
                        and params (dict of model params)
        """

        assert problem in ['classification', 'regression'], "problem must be 'classification' or 'regression'"
        self._get_best_model_name(problem=problem)
        self.model_params = self._get_best_model_params()
        result = self.db.execute(CLASS.substitute({'run_id': self._model_id}))
        try:
            model_class = result.__next__()[0]
            model_class = model_class.rsplit('.', 2)
            model_class = getattr(import_module(model_class[0]), model_class[-1])
            #self.model_params.pop('min_impurity_split', None)       # TODO: handle sklearn version conflict
            return self.model(model_class(**self.model_params), self.model_params)
        except (StopIteration, TypeError):
            return self.model(self.best_model_name, self.model_params)

    def get_meta_data(self) -> dict:
        """
        Function to return any calculated metrics on a model
        :return: dict of metrics (metrics depends on whether regression or classification model)
        """

        result = self.db.execute(METRICS.substitute({'run_id': self._model_id}))
        return {k: v for k, v in result}


if __name__ == '__main__':
    model = ModelGenerator()
    best_model = model.get_best_model(problem='classification')
    print(best_model.model)
    print(best_model.params)
    print(model.get_meta_data())



