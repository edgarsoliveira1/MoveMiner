from moveminer.core.Trajectory import Trajectory
from moveminer.utils import constants
from tensorflow import keras
import numpy as np


class TrajDeepFeedForward:
    def __init__(self, input_size, output_size) -> None:
        self.input_shape = (input_size,)
        self.output_size = output_size

        self.dff = keras.Sequential(
            [
                keras.layers.Dense(
                    256, activation="relu", input_shape=self.input_shape
                ),
                keras.layers.Dense(256, activation="relu"),
                keras.layers.Dropout(0.3),
                keras.layers.Dense(256, activation="relu"),
                keras.layers.Dropout(0.3),
                keras.layers.Dense(output_size, activation="sigmoid"),
            ]
        )

    def compile(
        self,
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=[
            keras.metrics.Accuracy(name="accuracy"),
            keras.metrics.Precision(name="precision"),
            keras.metrics.Recall(name="recall"),
        ],
    ):
        self.dff.compile(optimizer=optimizer, loss=loss, metrics=metrics)

    def fit(self, train_X, train_y, val_X, val_y, callbacks=[], class_weight={}):
        self.dff.fit(
            np.asarray(train_X).astype(np.float64),
            np.asarray(train_y).astype(np.float64),
            batch_size=2048,
            epochs=30,
            verbose=2,
            callbacks=callbacks,
            validation_data=(
                np.asarray(val_X).astype(np.float64),
                np.asarray(val_y).astype(np.float64),
            ),
            class_weight=class_weight,
        )

    def predict(self, test_X):
        return self.dff.predict(np.asarray(test_X).astype(np.float64)).astype(bool)
