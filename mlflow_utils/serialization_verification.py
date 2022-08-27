import mlflow
from xgboost import XGBClassifier
import pandas as pd
import numpy as np
import os
import shutil


if __name__ == '__main__':
    train_X = pd.DataFrame(np.random.normal(0, 1, (20, 8)))
    train_y = pd.DataFrame(np.random.binomial(1, .5, (20,)))
    test_X = pd.DataFrame(np.random.normal(0, 1, (2, 8)))
    original_model = XGBClassifier(use_label_encoder=False)
    original_model.fit(train_X, train_y)
    print("Model trained")
    model_file = "test_model"
    if os.path.exists(model_file):
        shutil.rmtree(model_file)
    mlflow.xgboost.save_model(original_model, model_file)
    print(f"Model saved to {model_file}")
    new_model = mlflow.pyfunc.load_model(model_file)
    try:
        assert (original_model.predict(test_X) == new_model.predict(test_X)).all()
        print("SUCCESS: Models are equal")
    except AssertionError:
        print("FAILURE: Models are not equivalent")

