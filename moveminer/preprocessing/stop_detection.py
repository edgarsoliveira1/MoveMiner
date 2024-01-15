from ..core.Trajectory import Trajectory
from ..utils import distance_metrics, constants


def distance_time(t: Trajectory, distance_threshold, time_threshold) -> [bool]:
    traj = t.copy()
    points = traj.gdf[constants.GEOMETRY]
    datetimes = traj.gdf.index
    stops = [True]
    i = 0
    while i < len(points) - 1:
        pid = points[i]
        pjd = points[i + 1]
        distance = traj.distance(pid, pjd)
        if distance <= distance_threshold:
            pit = datetimes[i]
            pjt = datetimes[i + 1]
            duration = (pjt - pit).total_seconds()
            if duration <= time_threshold:
                stops.append(True)
                i += 1
                continue
        stops.append(False)
        i += 1
    return stops


def speed(traj: Trajectory, speed_threshold) -> Trajectory:
    t = traj.copy()
    t_gdf = t.gdf.sort_values(by=[constants.DATETIME])
    t_gdf[constants.STOP] = False
    t_gdf[constants.SPEED] = 0
    points = t_gdf[constants.GEOMETRY]
    datetimes = t_gdf.index
    for i in range(len(points) - 1):
        pi = points[i]
        pj = points[i + 1]
        dist = t.distance(pi, pj) * 1000 # meters
        time = (datetimes[i + 1] - datetimes[i]).total_seconds() # seconds
        assert time > 0
        speed = dist / time # m/s
        t_gdf[constants.SPEED][i] = speed
        if speed <= speed_threshold:
            t_gdf[constants.STOP][i] = True
    t.gdf = t_gdf
    return t
