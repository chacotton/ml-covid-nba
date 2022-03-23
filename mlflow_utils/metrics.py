import sklearn.metrics as sm


def classification(y_true, y_pred) -> dict:
    """
    Returns classification metrics
    :param y_true: 1D array-like
    :param y_pred: 1D array-like
    :return: dict of accuracy, precision, auc, f1, and recall
    """
    return {
        'accuracy': sm.accuracy_score(y_true, y_pred),
        'precision': sm.precision_score(y_true, y_pred),
        'auc': sm.roc_auc_score(y_true, y_pred),
        'f1': sm.f1_score(y_true, y_pred),
        'recall': sm.recall_score(y_true, y_pred),
    }


def regression(y_true, y_pred) -> dict:
    """
    Returns regression metrics
    :param y_true: 1D array-like
    :param y_pred: 1D array-like
    :return: dict of r2, mse, mae, mape
    """
    return {
        'r2': sm.r2_score(y_true, y_pred),
        'mse': sm.mean_squared_error(y_true, y_pred, squared=True),
        'mae': sm.mean_absolute_error(y_true, y_pred),
        'mape': sm.mean_absolute_percentage_error(y_true, y_pred),
    }

