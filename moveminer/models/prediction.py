from moveminer.core.Trajectory import Trajectory
from moveminer.models.data_windowing import WindowGenerator
from moveminer.utils import constants
from tensorflow import keras
import numpy as np


class TrajLSTM:
    def __init__(self, lstm_units=100, return_sequences=True, dense_units=1) -> None:
        self.lstm = keras.models.Sequential(
            [
                # Shape [batch, time, features] => [batch, time, lstm_units]
                keras.layers.LSTM(lstm_units, return_sequences=return_sequences),
                # Shape => [batch, time, features]
                keras.layers.Dense(units=dense_units),
            ]
        )

    def compile_and_fit(self, window: WindowGenerator, epochs=100, patience=2):
        early_stopping = keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=patience, mode="min"
        )

        self.lstm.compile(
            loss=keras.losses.MeanSquaredError(),
            optimizer=keras.optimizers.Adam(),
            metrics=[keras.metrics.MeanAbsoluteError()],
        )

        history = self.lstm.fit(
            window.train,
            epochs=epochs,
            validation_data=window.val,
            callbacks=[early_stopping],
        )
        return history

    def evaluate(self, X, verbose=1):
        return self.lstm.evaluate(X, verbose=verbose)
