import numpy as np
import warnings
import math

warnings.filterwarnings("ignore")

rad = math.pi / 180.0
R = 6378137.0


def erp(traj_1: np.array, traj_2: np.array, g=None):
    dim_1 = traj_1.shape[1]
    dim_2 = traj_2.shape[1]

    if dim_1 != 2 or dim_2 != 2:
        raise ValueError(
            "Trajectories should be in 2D. t1 is %dD and t2 is %d given"
            % (dim_1, dim_2)
        )
    dim = dim_1

    if g is None:
        g = np.zeros(dim, dtype=float)
        warnings.warn("g parameter should be specified for metric erp. Default is ")
    else:
        if g.shape[0] != dim:
            raise ValueError("g and trajectories in list should have same dimension")

    dist = s_erp(traj_1, traj_2, g)
    return dist


def s_erp(t0, t1, g):
    n0 = len(t0)
    n1 = len(t1)
    C = np.zeros((n0 + 1, n1 + 1))

    C[1:, 0] = sum([abs(great_circle_distance(g[0], g[1], x[0], x[1])) for x in t0])
    C[0, 1:] = sum([abs(great_circle_distance(g[0], g[1], y[0], y[1])) for y in t1])
    for i in np.arange(n0) + 1:
        for j in np.arange(n1) + 1:
            derp0 = C[i - 1, j] + great_circle_distance(
                t0[i - 1][0], t0[i - 1][1], g[0], g[1]
            )
            derp1 = C[i, j - 1] + great_circle_distance(
                g[0], g[1], t1[j - 1][0], t1[j - 1][1]
            )
            derp01 = C[i - 1, j - 1] + great_circle_distance(
                t0[i - 1][0], t0[i - 1][1], t1[j - 1][0], t1[j - 1][1]
            )
            C[i, j] = min(derp0, derp1, derp01)
    erp = C[n0, n1]
    return erp


def great_circle_distance(lon1, lat1, lon2, lat2):
    dlat = rad * (lat2 - lat1)
    dlon = rad * (lon2 - lon1)
    a = math.sin(dlat / 2.0) * math.sin(dlat / 2.0) + math.cos(rad * lat1) * math.cos(
        rad * lat2
    ) * math.sin(dlon / 2.0) * math.sin(dlon / 2.0)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    return d
