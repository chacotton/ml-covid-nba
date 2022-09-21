from xgboost import XGBClassifier
import mlflow
import numpy as np
from warnings import warn
from argparse import ArgumentParser


class XGBWrapper(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        from xgboost import XGBClassifier
        self.model = XGBClassifier()
        self.model.load_model(context.artifacts["xgb"])
    def predict(self, context, model_input):
        return self.model.predict_proba(model_input)[:,1]


def xgb_load(file):
    m = XGBClassifier()
    m.load_model(file)
    input_width = m.n_features_in_
    return m, input_width


models = {
    'xgb': xgb_load,
}

serialize = {
    'xgb': lambda x,y: mlflow.pyfunc.save_model(x, python_model=XGBWrapper(), artifacts={'xgb':y}),
}

if __name__ == '__main__':
    parser = ArgumentParser('Serialization Script')
    parser.add_argument('--file', type=str, help='file to serialize')
    parser.add_argument('--model', type=str, default='xgb', help='supported types: {xgb}')
    parser.add_argument('--output', type=str, help='name of output file')
    args = parser.parse_args()
    assert args.file is not None, "Please Pass a Model File"
    print('[1/2] Model Verification Begins ...')
    model_file = args.file
    output = args.output
    model, input_size = models.get(args.model, 'xgb')(model_file)
    input_data = np.random.normal(0, 1, (1, input_size))
    pred = model.predict_proba(input_data)[:,1]
    assert 0 <= pred <= 1
    print('[1/2] Model Verified')
    print('[2/2] MLFlow Serialization Begins ...')
    serialize.get(args.model, 'xgb')(output, model_file)
    test_model = mlflow.pyfunc.load_model(output)
    test_pred = test_model.predict(input_data)
    if not (pred == test_pred).all():
        warn("Serialized Model is NOT Equivalent")
    print('[2/2] MLFlow Serialization Complete')


