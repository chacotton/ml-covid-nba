from modeling import NBAModel


class NBACovid(NBAModel):
    """
    Class Implementation of NBA Covid Recovery Model

    Loads Covid Recovery Model and writes prediction to database
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def predict(self, x: dict) -> float:
        return 0.0

    # TODO: other methods
