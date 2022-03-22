import mysql.connector


class ModelGenerator:
    def __init__(self, database="test_db"):
        self.db = mysql.connector.connect(
                host="10.0.0.150",
                user="admin",
                password="NBACovid19!",
                database=database,
                )
        self.best_model_name = None
        self.model_params = None
        self.meta_data = None

    def _get_best_model_name(self):
        raise NotImplementedError

    def _get_best_model_params(self):
        raise NotImplementedError

    def get_best_model(self):
        raise NotImplementedError

    def get_meta_data(self):
        raise NotImplementedError


if __name__ == '__main__':
    db = mysql.connector.connect(
        host="10.0.0.150",
        user="admin",
        password="NBACovid19!",
        database="test_db",
    )
    with db.cursor() as cur:
        cur.execute("SELECT * FROM tags WHERE `key` = 'mlflow.autologging'")
        for x in cur:
            print(x)
    db.close()

