import tensorflow as tf
import numpy as np
from tqdm.auto import tqdm
from random import shuffle
import logging
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # FATAL
logging.getLogger('tensorflow').setLevel(logging.FATAL)


def model_generator(lr=.001, neurons=500, input_length=5, features=1):
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(neurons, activation='sigmoid', input_shape=(input_length, features)),
        tf.keras.layers.Dense(1, activation='sigmoid'),
    ])
    model.compile(optimizer=tf.keras.optimizers.Adam(lr), loss=tf.keras.losses.MeanSquaredError())
    return model


class Serial:

    def __init__(self, neurons=500, lr=.001):
        self.model = None
        self.neurons = neurons
        self.lr = lr
        self.lag = None

    def fit(self, data, lag=12, epochs=10, **kwargs):
        assert data.ndim == 3
        self.lag = lag
        self.model = model_generator(input_length=lag, features=data.shape[-1], lr=self.lr, neurons=self.neurons)
        ts_data = [
            tf.keras.preprocessing.sequence.TimeseriesGenerator(data[i], data[i, :, 0], length=lag, batch_size=32) for
            i in range(len(data))]
        for _ in tqdm(range(epochs)):
            shuffle(ts_data)
            for data in ts_data:
                self.model.fit(data, steps_per_epoch=len(ts_data), epochs=1, verbose=0)
        return self

    def predict(self, data):
        yhat = self.model.predict(tf.keras.preprocessing.sequence.TimeseriesGenerator(data, data[:, 0], length=self.lag, batch_size=1))
        return yhat


class Average:

    def __init__(self, neurons=500, lr=.001):
        self.model = None
        self.neurons = neurons
        self.lr = lr
        self.lag = None

    def fit(self, data, lag=12, epochs=10, **kwargs):
        assert data.ndim == 3
        self.lag = lag
        self.model = [model_generator(input_length=lag, features=data.shape[-1], **kwargs) for _ in range(len(data))]
        ts_data = [
            tf.keras.preprocessing.sequence.TimeseriesGenerator(data[i], data[i, :, 0], length=lag, batch_size=32) for
            i in range(len(data))]
        for _ in tqdm(range(epochs)):
            for m, x in zip(self.model, ts_data):
                m.fit(x, steps_per_epoch=len(x), epochs=1, verbose=0)
        return self

    def predict(self, data):
        yhat = []
        for model in self.model:
            yhat.append(model.predict(tf.keras.preprocessing.sequence.TimeseriesGenerator(data, data[:, 0], length=self.lag, batch_size=1)))
        yhat = np.array(yhat)
        return np.mean(yhat, axis=0)


class FederatedAverage:

    def __init__(self, neurons=500, lr=.001):
        self.model = None
        self.neurons = neurons
        self.lr = lr
        self.lag = None

    def fit(self, data, lag=12, epochs=10, **kwargs):
        assert data.ndim == 3
        self.lag = lag
        self.model = model_generator(input_length=lag, features=data.shape[-1], **kwargs)
        models = [model_generator(input_length=lag, features=data.shape[-1], **kwargs) for _ in range(len(data))]
        ts_data = [tf.keras.preprocessing.sequence.TimeseriesGenerator(data[i], data[i, :, 0], length=lag, batch_size=32) for
                i in range(len(data))]
        for _ in tqdm(range(epochs)):
            for m, x in zip(models, ts_data):
                m.fit(x, steps_per_epoch=len(x), epochs=1, verbose=0)
            weights = [np.mean([m.get_weights()[i] for m in models], axis=0) for i in range(len(self.model.get_weights()))]
            self.model.set_weights(weights)
            for m in models:
                m.set_weights(weights)
        return self

    def predict(self, data):
        yhat = self.model.predict(tf.keras.preprocessing.sequence.TimeseriesGenerator(data, data[:, 0], length=self.lag, batch_size=1))
        return yhat


