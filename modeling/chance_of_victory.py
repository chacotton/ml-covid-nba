from modeling import NBAModel


class NBACoV(NBAModel):
    """
    Class Implementation of NBA Chance of Victory Model

    Loads Chance of Victory Model and writes prediction to database
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def predict(self, x: dict) -> float:
        return 0.0

    # TODO: other methods
