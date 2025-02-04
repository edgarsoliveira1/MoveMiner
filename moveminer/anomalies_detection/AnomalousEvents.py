from sklearn.neighbors import LocalOutlierFactor
from moveminer.core.Trajectory import Trajectory
from moveminer.utils import constants


class AnomalousEvents:
    def __init__(
        self, features=[constants.LATITUDE, constants.LONGITUDE, constants.SPEED]
    ) -> None:
        self.features = features

    def anomalous_events(self, traj: Trajectory, outlier_threshold: float):
        t = traj.copy()
        t.gdf[constants.OUTLIER_SCORE] = 0
        for cluster_uid in t.gdf[constants.CLUSTER].unique():
            cluster = t.gdf[t.gdf[constants.CLUSTER] == cluster_uid]
            if len(cluster) < 2:
                continue
            LOF = LocalOutlierFactor()
            pred = LOF.fit_predict(cluster[self.features])
            outlier_score = pred.mean()
            cluster[constants.OUTLIER_SCORE] = outlier_score
            t.gdf[t.gdf[constants.CLUSTER] == cluster_uid] = cluster
        outliers = t.gdf[constants.OUTLIER_SCORE].apply(lambda o: o > outlier_threshold)
        t.gdf[constants.OUTLIER] = outliers
        return t
