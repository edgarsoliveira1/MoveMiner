from moveminer.core.Trajectory import Trajectory
from moveminer.utils import constants


class DistanceSegmentation:
    def __init__(self, threshold_m: float) -> None:
        self.threshold_m = threshold_m
        pass

    def segment(self, traj: Trajectory) -> Trajectory:
        t = traj.copy()
        t_gdf = t.gdf
        seg_count = 0
        dist_sum = 0
        t_gdf[constants.SEGMENT] = seg_count
        for i in range(len(t_gdf) - 1):
            point_i = t_gdf.iloc[i][constants.GEOMETRY]
            point_j = t_gdf.iloc[i + 1][constants.GEOMETRY]
            dist = traj.distance(point_i, point_j)  # km
            dist = dist * 1000  # m
            dist_sum += dist
            if dist_sum > self.threshold_m:
                seg_count += 1
                dist_sum = 0
            t_gdf[constants.SEGMENT][i] = seg_count
        t.gdf = t_gdf
        return t


class TimeSegmentation:
    def __init__(self, threshold_s: float) -> None:
        self.threshold_s = threshold_s
        pass

    def segment(self, traj: Trajectory) -> Trajectory:
        t = traj.copy()
        t_gdf = t.gdf
        seg_count = 0
        time_sum = 0
        t_gdf[constants.SEGMENT] = seg_count
        for i in range(len(t_gdf) - 1):
            time_i = t_gdf.iloc[i].index
            time_j = t_gdf.iloc[i + 1].index
            interval = (time_j - time_i).total_seconds()  # seconds
            time_sum += interval
            if time_sum > self.threshold_s:
                seg_count += 1
                time_sum = 0
            t_gdf[constants.SEGMENT][i] = seg_count
        t.gdf = t_gdf
        return t


class StopSegmentation:
    def __init__(self) -> None:
        pass

    def segment(self, traj: Trajectory) -> Trajectory:
        if constants.STOP not in traj.gdf.columns:
            raise Exception("Trajectory does not have stop column")
        t = traj.copy()
        t_gdf = t.gdf
        seg_count = 0
        t_gdf[constants.SEGMENT] = seg_count
        for i in range(len(t_gdf) - 1):
            stop_i = t_gdf.iloc[i][constants.STOP]
            stop_j = t_gdf.iloc[i + 1][constants.STOP]
            if not stop_i and stop_j:
                seg_count += 1
            if not stop_i:
                t_gdf[constants.SEGMENT][i] = seg_count
        t.gdf = t_gdf
        return t
