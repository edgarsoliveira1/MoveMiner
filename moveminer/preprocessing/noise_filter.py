from ..utils import distance_metrics, constants
from ..core.Trajectory import Trajectory
from shapely.geometry import Point
import pandas as pd


class LinearSpeedBounded:
    def __init__(self, threshold):
        self.threshold = threshold
        self.distance = distance_metrics.euclidean

    def __call__(self, p1, p2) -> bool:
        id, g1, t1 = p1
        id, g2, t2 = p2
        tdiff = (t2 - t1).total_seconds()
        if not tdiff > 0:
            return False
        dist = self.distance(g1, g2) * 1000
        return dist / tdiff >= self.threshold


# Maximum Physically Consist Trajectories
# published in SIGSPATIAL 2019
class MPCT:
    def __init__(self, Predicate, threshold):
        self.threshold = threshold
        self._Predicate = Predicate
        self.predicate = Predicate(threshold)

    def _mpct(self, input_data: Trajectory):
        sequences = []

        for item in input_data:
            extend_subsequence = False

            for sequence in sequences:
                prev = sequence[-1] if sequence else None

                if prev is not None and self.predicate(prev, item):
                    sequence.append(item)
                    extend_subsequence = True

            if not extend_subsequence:
                sequences.append([item])

        sequences.sort(key=lambda seq: len(seq), reverse=True)

        max_size = len(sequences[0])
        sequences = [seq for seq in sequences if len(seq) == max_size]

        return sequences

    def predict(self, traj: Trajectory):
        # set the right distance metric
        self.predicate.distance = traj.distance
        gdf = traj.gdf
        # predict the noise/outlier
        df = pd.DataFrame()
        df["inx"] = gdf[constants.COUNT]
        df["geo"] = gdf[constants.GEOMETRY]
        df["t"] = gdf.index
        trajectory = df[["inx", "geo", "t"]].values
        sequences = self._mpct(trajectory)
        df["pred"] = False
        stop_indexes = []
        for s in sequences[0]:
            stop_indexes.append(s[0])
        stops = df["inx"].isin(stop_indexes)
        df.loc[stops, "pred"] = True
        return df["pred"]


def speed_filter(t: Trajectory, speed_threshold=0) -> Trajectory:
    traj = t.copy()
    mpct = MPCT(LinearSpeedBounded, speed_threshold)
    traj.gdf[constants.NOISE] = mpct.predict(traj)
    traj.gdf = traj.gdf[traj.gdf[constants.NOISE] == False]
    traj.gdf.drop(columns=[constants.NOISE], inplace=True)
    return traj
