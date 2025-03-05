# (Strategy Pattern)
from abc import ABC, abstractmethod
from typing import Union

import dask.dataframe as dd
import datashader as ds
import holoviews as hv
import hvplot.dask
from datashader.colors import viridis
from holoviews.operation import datashader as hvds

from ..core.trajectory import Trajectory
from ..utils import geo_utils
from ..utils.config import col_names


class SpatialPlotStrategy(ABC):
    @abstractmethod
    def plot(self, trajectory_data: Trajectory):
        raise NotImplementedError("Subclasses should implement this method")


# class AggPointDynamicStrategy(SpatialPlotStrategy):
#     def plot(
#         self, trajectory_data: Trajectory, cmap=viridis
#     ) -> Union[hv.Element, hv.Overlay]:
#         if trajectory_data.is_geo:
#             trajectory_data = geo_utils.project_to_web_mercator(
#                 trajectory_data.copy()
#             )
#         points = hv.Points(
#             trajectory_data,
#             kdims=[col_names.X, col_names.Y],
#         )
#         pointshaded = hvds.datashade(points, cmap=cmap, how="eq_hist")
#         return pointshaded


# class AggPointStaticStrategy(SpatialPlotStrategy):
#     def plot(
#         self, trajectory_data: Trajectory, cmap=viridis
#     ) -> Union[hv.Image]:
#         if trajectory_data.is_geo:
#             trajectory_data = geo_utils.project_to_web_mercator(
#                 trajectory_data.copy()
#             )
#         # Esse plot parece ter um resolução melhor, por quê?
#         cvs = ds.Canvas(plot_width=850, plot_height=850)
#         agg = cvs.points(trajectory_data, col_names.X, col_names.Y)
#         return ds.tf.shade(agg, cmap=cmap, how="eq_hist")


class PointPlotStrategy(SpatialPlotStrategy):
    def plot(
        self, trajectory_data: Trajectory, *args, **kwargs
    ) -> Union[hv.Element, hv.Overlay]:
        if trajectory_data.is_geo:
            trajectory_data = geo_utils.project_to_web_mercator(trajectory_data.copy())
        return dd.from_pandas(trajectory_data, npartitions=2).hvplot.points(
            col_names.X, col_names.Y, *args, **kwargs
        )


class PointPlotter:
    def __init__(self, strategy: SpatialPlotStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: SpatialPlotStrategy):
        self._strategy = strategy

    def plot(
        self,
        trajectory_data: Trajectory,
        *args,
        **kwargs,
    ) -> Union[hv.Element, hv.Overlay]:
        return self._strategy.plot(trajectory_data, *args, **kwargs)
