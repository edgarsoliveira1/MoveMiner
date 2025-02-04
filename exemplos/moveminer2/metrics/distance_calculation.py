# (Strategy Pattern)
from abc import ABC, abstractmethod

import dask.dataframe as dd
import numpy as np
import pandas as pd

from ..core.trajectory import Trajectory
from ..utils.config import col_names, constants
from ..utils.utils import set_unique_index


# Estratégia de cálculo de distancia entre pontos
class DistanceCalculationStrategy(ABC):
    @abstractmethod
    def calculate(self, x1, y1, x2, y2) -> float:
        """
        Abstract method to calculate the distance between consecutive points in a trajectory.

        Parameters:
        trajectory (TrajectoryData): The trajectory data containing the coordinates of the points.

        Returns:
        TrajectoryData: The trajectory data with an additional column containing the calculated distances.
        """
        raise NotImplementedError


class EuclideanDistanceCalculation(DistanceCalculationStrategy):
    def calculate(self, x1, y1, x2, y2) -> float:
        # Implementação de distância euclidiana
        x_diff = x1 - x2
        y_diff = y1 - y2
        return np.sqrt(x_diff**2 + y_diff**2)


class HaversineDistanceCalculation(DistanceCalculationStrategy):
    def calculate(self, lat1, lon1, lat2, lon2) -> float:
        # Implementação de distância Haversine
        R = constants.R  # Radius of the Earth in meters
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            np.sin(dlat / 2.0) ** 2
            + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
        )

        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        return R * c


class DistanceCalculator:
    def __init__(self, strategy: DistanceCalculationStrategy):
        if strategy is DistanceCalculationStrategy:
            self._strategy = strategy()
        else:
            self._strategy = strategy

    def set_strategy(self, strategy: DistanceCalculationStrategy):
        self._strategy = strategy

    def calculate_total_distance(self, trajectory: Trajectory) -> pd.DataFrame:
        # Ensure that the distance column is present
        if col_names.DISTANCE not in trajectory.columns:
            trajectory = self.add_distance_column(trajectory)
        return trajectory.groupby(col_names.TRAJECTORY_ID).apply(
            lambda t: t[col_names.DISTANCE].sum()
        )

    def calculate_straight_line_distance(self, trajectory: Trajectory) -> pd.DataFrame:
        def calculate_group_straight_line_distance(group: pd.DataFrame):
            point1 = group.iloc[[0]]
            point2 = group.iloc[[-1]]
            return self._strategy.calculate(
                point1[col_names.X],
                point1[col_names.Y],
                point2[col_names.X],
                point2[col_names.Y],
            )

        return trajectory.groupby(col_names.TRAJECTORY_ID).apply(
            calculate_group_straight_line_distance
        )

    def calculate_radius_of_gyration(self, trajectory: Trajectory) -> Trajectory:
        trajectory["x_mean"] = trajectory.groupby(col_names.TRAJECTORY_ID)[
            col_names.X
        ].transform("mean")
        trajectory["y_mean"] = trajectory.groupby(col_names.TRAJECTORY_ID)[
            col_names.Y
        ].transform("mean")
        trajectory = dd.from_pandas(
            trajectory, npartitions=trajectory.npartitions, sort=True
        )
        trajectory["squared_radius_distance"] = trajectory.map_partitions(
            lambda d: self._strategy.calculate(
                d["y_mean"],
                d["x_mean"],
                d[col_names.Y],
                d[col_names.X],
            )
            ** 2,
            meta=("radius_distance", "f8"),
        ).fillna(0)
        trajectory = trajectory
        return (
            trajectory.groupby(col_names.TRAJECTORY_ID)["squared_radius_distance"]
            .transform("mean")
            .apply(np.sqrt)
        ).compute()

    def add_distance_column(self, trajectory: Trajectory) -> Trajectory:
        trajectory[col_names.PREV_X] = trajectory.groupby(col_names.TRAJECTORY_ID)[
            col_names.X
        ].shift(1)
        trajectory[col_names.PREV_Y] = trajectory.groupby(col_names.TRAJECTORY_ID)[
            col_names.Y
        ].shift(1)
        trajectory = dd.from_pandas(trajectory, npartitions=trajectory.npartitions)
        trajectory[col_names.DISTANCE] = trajectory.map_partitions(
            lambda d: self._strategy.calculate(
                d[col_names.PREV_Y],
                d[col_names.PREV_X],
                d[col_names.Y],
                d[col_names.X],
            ),
            meta=(col_names.DISTANCE, "f8"),
        )
        return trajectory.compute()
