# (Strategy Pattern)
from abc import ABC, abstractmethod

import dask.dataframe as dd
import pandas as pd
from numpy import isnat

from ..utils.config import col_names


# Estratégia de cálculo de delta time entre pontos
class TimeDiffCalculationStrategy(ABC):
    @abstractmethod
    def calculate(self, t1: pd.Series, t2: pd.Series) -> pd.Series:
        """
        Calcula a distância entre dois pontos.

        Parameters:
        point_a (pd.Series): Um ponto com colunas 'x', 'y' e 't'.
        point_b (pd.Series): Outro ponto com colunas 'x', 'y' e 't'.

        Returns:
        float: A diferença de tempo calculada entre os dois pontos em segundos.
        """
        raise NotImplementedError


class SimpleTimeDiffCalculation(TimeDiffCalculationStrategy):
    def calculate(self, t1: pd.Series, t2: pd.Series) -> pd.Series:
        time_diff = (t2 - t1).dt.total_seconds()
        return time_diff.fillna(0)


class TimestampTimeDiffCalculation(TimeDiffCalculationStrategy):
    def calculate(self, point_a: pd.Series, point_b: pd.Series) -> float:
        time_diff = (
            pd.Timestamp(point_b[col_names.T]) - pd.Timestamp(point_a[col_names.T])
        ).dt.total_seconds()
        return time_diff


class TimeDiffCalculator:
    def __init__(self, strategy: TimeDiffCalculationStrategy):
        if strategy is TimeDiffCalculationStrategy:
            self._strategy = strategy()
        else:
            self._strategy = strategy

    def set_strategy(self, strategy: TimeDiffCalculationStrategy):
        self._strategy = strategy

    def calculate_total_time(self, trajectory: pd.DataFrame) -> float:
        def calculate_group_total_time(group: pd.DataFrame):
            point1 = group.iloc[[0]]
            point2 = group.iloc[[-1]]
            return self._strategy.calculate(
                point1[col_names.T],
                point2[col_names.T],
            )

        return trajectory.groupby(col_names.TRAJECTORY_ID).apply(
            calculate_group_total_time
        )

    def add_timediff_column(self, trajectory: pd.DataFrame) -> pd.DataFrame:
        # Function to calculate time difference within each group
        trajectory[col_names.PREV_T] = trajectory.groupby(col_names.TRAJECTORY_ID)[
            col_names.T
        ].shift(1)

        # Apply the function to each group
        trajectory = dd.from_pandas(trajectory, npartitions=trajectory.npartitions)
        trajectory[col_names.TIME_DIFF] = trajectory.map_partitions(
            lambda d: self._strategy.calculate(
                d[col_names.PREV_T],
                d[col_names.T],
            ),
            meta=(col_names.TIME_DIFF, "f8"),
        )
        return trajectory.compute()
