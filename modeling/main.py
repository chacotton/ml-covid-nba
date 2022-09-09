from argparse import ArgumentParser
import mlflow
import pandas as pd
import numpy as np

if __name__ == '__main__':
    parser = ArgumentParser("Modeling")
    parser.add_argument('--model', type=str)
    args = parser.parse_args()
    model_path = args.model
    test_X = pd.DataFrame(np.random.normal(0, 1, (4, 8)))
    model = mlflow.pyfunc.load_model(model_path)
    model.predict(test_X)
    print('SUCCESS')

