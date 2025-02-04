from abc import ABCMeta, abstractmethod
from moveminer.core.Trajectory import Trajectory
from moveminer.utils import constants


class ProspectivePattern(object):
    __metaclass__ = ABCMeta

    def __init__(self, m, r) -> None:
        self.m = m
        self.r = r

    @abstractmethod
    def run(self, traj: Trajectory):
        pass


class Encounter(ProspectivePattern):
    """
    A group of at least m objects that will arrive simultaneously in a disc with radius r
    """

    def __init__(self, m, r):
        super(Encounter, self).__init__(m, r)

    def run(self, traj: Trajectory):
        t = traj.copy()
        tgdf = t.gdf
        tgdf[constants.ENCOUNTER] = ""
        if not t.is_multuid:
            return t
        tgdf.sort_values(by=[constants.UID, constants.DATETIME])
        last_points = tgdf.groupby(constants.UID).tail(1)
        encounter_count = 1
        for i in range(len(last_points)):
            last_point = last_points.iloc[i]
            area = last_point[constants.GEOMETRY].buffer(self.r)
            close_points = last_points.clip(area)
            if len(close_points) >= self.m:
                tgdf_c = tgdf[constants.COUNT]
                close_points_c = close_points[constants.COUNT]
                tgdf.loc[tgdf_c.isin(close_points_c), constants.ENCOUNTER] += " " + str(
                    encounter_count
                )
                encounter_count += 1
        return t


class Convergence(ProspectivePattern):
    """
    A group of at least m objects that will pass through a disc with radius r (not necessarily at the same time).
    """

    def __init__(self, m, r):
        super(Convergence, self).__init__(m, r)

    def run(self, traj: Trajectory):
        # TODO
        pass
