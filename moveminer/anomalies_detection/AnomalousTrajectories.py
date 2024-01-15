from sklearn.neighbors import LocalOutlierFactor
from moveminer.core.Trajectory import Trajectory
from moveminer.utils import constants

class DetectOutlierTrajectory():
  def __init__(self) -> None:
    pass
  def detect_outlier_trajectory(self, traj:Trajectory, outlier_threshold:float):
    t = traj.copy()
    t.gdf[constants.TRAJ_OUTLIER_SCORE] = 0
    t.gdf[constants.TRAJ_OUTLIER] = False
    for uid in t.gdf[constants.UID].unique():
      tuid = t.gdf[t.gdf[constants.UID] == uid]
      traj_outlier_score = tuid[constants.OUTLIER_SCORE].mean()
      tuid[constants.TRAJ_OUTLIER_SCORE] = traj_outlier_score
      t.gdf[t.gdf[constants.UID] == uid] = tuid
      if traj_outlier_score >= outlier_threshold:
        t.gdf[constants.TRAJ_OUTLIER] = True
    return t
