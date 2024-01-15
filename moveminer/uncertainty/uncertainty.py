from shapely import LineString, Point, simplify
from ..core.Trajectory import Trajectory
from scipy import signal

def smoother(trj, w: int = None, p: int = 3):
    if w is None:
        w = p + 3 - p % 2
    if w % 2 != 1:
        raise Exception(f"Invalid smoothing parameter w ({w}): n must be odd")
    _trj = trj.copy()
    x = signal.savgol_filter( _trj.gdf['geometry'].x, window_length=w, polyorder=p, axis=0)
    y = signal.savgol_filter( _trj.gdf['geometry'].y, window_length=w, polyorder=p, axis=0)
    for i in range(len(_trj.gdf)):
        _trj.gdf['geometry'][i] = Point(x[i], y[i])
    return _trj 