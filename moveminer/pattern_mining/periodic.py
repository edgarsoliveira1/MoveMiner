from moveminer.core.Trajectory import Trajectory
from moveminer.utils import constants
from datetime import timedelta
import pandas as pd

class Periodic:
    def __init__(self, period=timedelta(days=1), bin=timedelta(hours=1)) -> None:
        self.period = period
        self.bin = bin
    
    def periodic(self, t: Trajectory) -> pd.DataFrame:
        traj = t.copy()
        if not constants.CLUSTER in traj.gdf.columns:
            return pd.DataFrame()
        clusters_mobility = pd.get_dummies(traj.gdf[[constants.CLUSTER]],
                                           columns=[constants.CLUSTER])
        start_time = clusters_mobility.head(1).index
        end_time = clusters_mobility.tail(1).index
        bin_length = int(self.period/self.bin)
        bin_values = [pd.Series() for _ in range(bin_length)]
        for i in range(bin_length):
            period_i = 1
            curr_time = start_time
            a = curr_time
            b = curr_time + self.bin
            bin_values[i] = clusters_mobility.loc[a[0]: b[0]].sum()
            while curr_time < end_time:
                curr_time += self.period * period_i
                bin_offset = (self.bin * i)
                a = curr_time + bin_offset 
                b = curr_time + self.bin + bin_offset
                bin_values[i] += clusters_mobility.loc[a[0]: b[0]].sum()
        return pd.DataFrame(bin_values)