from moveminer.core.Trajectory import Trajectory
from moveminer.management.erp import erp
from shapely import LineString, Point
from moveminer.utils import constants
from datetime import datetime
import numpy as np


def spacial_query(
    t: Trajectory, xmin: float, ymin: float, xmax: float, ymax: float
) -> Trajectory:
    query = t.copy()
    query.gdf["geometry"] = query.gdf.clip_by_rect(xmin, ymin, xmax, ymax)
    query.gdf = query.gdf[~query.gdf.is_empty]
    return query


def temporal_query(t: Trajectory, start, end) -> Trajectory:
    query = t.copy()
    if not isinstance(start, datetime):
        start = datetime.fromisoformat(start).time()
    if not isinstance(end, datetime):
        end = datetime.fromisoformat(end).time()
    query.gdf = query.gdf.between_time(start, end)
    return query


def knn_query(t: Trajectory, k: int, geo: Point | LineString):
    query = t.copy()
    gdf = query.gdf
    distances = []
    for point in gdf[constants.GEOMETRY]:
        distance = geo.distance(point)
        distances.append(distance)
    query.gdf[constants.DISTANCE] = distances
    query.gdf = query.gdf.sort_values(by=constants.DISTANCE).head(k)
    return query


def _trajectory2npArray(t: Trajectory):
    x = t.gdf[constants.GEOMETRY].x
    y = t.gdf[constants.GEOMETRY].y
    return np.column_stack([x, y])


def similarity_query(t: Trajectory, TS: [Trajectory]):
    closest_trajectory = None
    smallest_distance = 0
    for ts in TS:
        traj_A = _trajectory2npArray(t)
        traj_B = _trajectory2npArray(ts)
        distance = erp(traj_A, traj_B, None)
        if smallest_distance < distance:
            closest_trajectory = ts
            smallest_distance = distance
    return closest_trajectory
