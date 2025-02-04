from moveminer.core.Trajectory import Trajectory
from sklearn import cluster
from moveminer.utils import constants
import numpy as np


class DBSCAN:
    def __init__(
        self, cluster_radius_km=0.1, min_samples=1, kms_per_radian=6371
    ) -> None:
        self.cluster_radius_km = cluster_radius_km
        self.min_samples = min_samples
        self.kms_per_radian = kms_per_radian
        self.eps = cluster_radius_km / kms_per_radian

    def db_scan(self, traj: Trajectory):
        t = traj.copy()
        t.gdf = t.gdf.sort_values(by=constants.DATETIME)
        db = cluster.DBSCAN(
            eps=self.eps,
            min_samples=self.min_samples,
            algorithm="ball_tree",
            metric="haversine",
        )
        t.gdf[constants.CLUSTER] = -1
        for uid in t.gdf[constants.UID].unique():
            coords = t.gdf[t.gdf[constants.UID] == uid][
                [constants.LATITUDE, constants.LONGITUDE]
            ].values
            db.fit(np.radians(coords))
            t.gdf.loc[t.gdf[constants.UID] == uid, constants.CLUSTER] = db.labels_
        return t


class KMeans:
    def __init__(self, n_clusters=8) -> None:
        self.n_clusters = n_clusters

    def k_means(self, traj: Trajectory):
        t = traj.copy()
        model = cluster.KMeans(n_clusters=self.n_clusters)
        coords = t.gdf[[constants.LATITUDE, constants.LONGITUDE]].values
        model.fit(np.radians(coords))
        t.gdf[constants.CLUSTER] = model.labels_
        return t
