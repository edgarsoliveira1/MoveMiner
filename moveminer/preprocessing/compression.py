from moveminer.core.Trajectory import Trajectory
from shapely.geometry import LineString
from moveminer.utils import constants

class SimpleSpacialCompression:
    def __init__(self, threshold: float):
        self.threshold = threshold
    
    def __call__(self, traj: Trajectory) -> Trajectory:
        t = traj.copy()
        gdf = t.gdf
        if len(gdf) < 3:
            return t
        i = 0
        while i < len(gdf) - 1:
            pi = gdf.iloc[[i]]
            close_points = [pi[constants.COUNT]]
            j = i + 1
            while j < len(gdf):
                pj = gdf.iloc[[j]]
                distance = t.distance(pi[constants.GEOMETRY], pj[constants.GEOMETRY])
                if distance < self.threshold:
                    close_points.append(pj[constants.COUNT])
                    j += 1
                    continue
                break
            if len(close_points) > 1:
                close_geo = gdf[constants.COUNT].isin(close_points)
                gdf[constants.GEOMETRY][i] = LineString(gdf[close_geo]).centroid
                i = j + 1
                continue
            i += 1
        return t