from modeling import NBAModel
import pytest


class TestNBAModel:
    def test_init(self):
        with pytest.raises(TypeError):
            NBAModel()

# TODO: Test static & class methods
