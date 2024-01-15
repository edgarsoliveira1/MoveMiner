from sklearn.model_selection import train_test_split as _train_test_split
from moveminer.core.Trajectory import Trajectory
from moveminer.utils import constants

def train_test_split(traj: Trajectory, test_size=0.4, random_state=0):
    t = traj.copy()
    t_gdf = t.gdf
    if traj.is_multuid:
        train_ids, test_ids = _train_test_split(t_gdf[constants.UID].unique(),
                                                test_size=test_size, 
                                                random_state=random_state)
        train_data = t_gdf[t_gdf[constants.UID].isin(train_ids)]
        test_data = t_gdf[t_gdf[constants.UID].isin(test_ids)]
    else:
        train_data, test_data = _train_test_split(t_gdf, test_size=test_size,
                                        random_state=random_state, shuffle=False)
    t_train = Trajectory(train_data, geo=t.geo)
    t_test = Trajectory(test_data, geo=t.geo)
    return t_train, t_test
