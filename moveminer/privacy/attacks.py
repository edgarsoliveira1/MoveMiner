from abc import ABCMeta, abstractmethod
from itertools import combinations
from ..utils import constants
from ..core import Trajectory
from tqdm import tqdm
import pandas as pd


class Attack(object):
    __metaclass__ = ABCMeta

    def __init__(self, knowledge_length=1):
        self.knowledge_length = knowledge_length

    # @property
    # def knowledge_length(self):
    #     return self._knowledge_length

    # @knowledge_length.setter
    # def knowledg_length(self, val):
    #     if val < 1:
    #         raise ValueError('Parameter knowledge_length should not be less than 1')
    #     self._knowledge_length = val

    def _all_risks(
        self, traj, targets=None, force_instances=False, show_progress=False
    ):
        # define targets
        if targets is None:
            targets = traj
        else:
            if isinstance(targets, list):
                targets = traj[traj[constants.UID].isin(targets)]
            if isinstance(targets, Trajectory):
                targets = traj[traj[constants.UID].isin(targets.gdf[constants.UID])]
        # compute risk
        if show_progress:
            tqdm.pandas(desc="computing risk")
            risks = targets.groupby(constants.UID).progress_apply(
                lambda x: self._risk(x, traj, force_instances)
            )
        else:
            risks = targets.groupby(constants.UID).apply(
                lambda x: self._risk(x, traj, force_instances)
            )
        # reset index
        if force_instances:
            risks = risks.droplevel(1)
            risks = risks.reset_index(drop=True)
        else:
            risks = risks.reset_index(name=constants.PRIVACY_RISK)
        return risks

    def _generate_instances(self, single_traj):
        size = len(single_traj)
        if self.knowledge_length > size:
            return combinations(single_traj.values, size)
        else:
            return combinations(single_traj.values, self.knowledge_length)

    def _risk(self, single_traj, traj, force_instances=False):
        instances = self._generate_instances(single_traj)
        risk = 0
        if force_instances:
            inst_data = {
                constants.LATITUDE: list(),
                constants.LONGITUDE: list(),
                constants.DATETIME: list(),
                constants.UID: list(),
                constants.INSTANCE: list(),
                constants.INSTANCE_ELEMENT: list(),
                constants.PROBABILITY: list(),
            }
            inst_id = 1
            for instance in instances:
                prob = (
                    1.0 / traj.groupby().apply(lambda x: self._match(x, instance)).sum()
                )
                elem_count = 1
                for elem in instance:
                    inst_data[constants.LATITUDE].append(elem[0])
                    inst_data[constants.LONGITUDE].append(elem[1])
                    inst_data[constants.DATETIME].append(elem[2])
                    inst_data[constants.UID].append(elem[3])
                    inst_data[constants.INSTANCE].append(inst_id)
                    inst_data[constants.INSTANCE_ELEMENT].append(elem_count)
                    inst_data[constants.PROBABILITY].append(prob)
                    elem_count += 1
                inst_id += 1
            return pd.DataFrame(inst_data)
        else:
            for instance in instances:
                prob = (
                    1.0
                    / traj.groupby(constants.UID)
                    .apply(lambda x: self._match(x, instance))
                    .sum()
                )
                if prob > risk:
                    risk = prob
                if risk == 1.0:
                    break
            return risk

    @abstractmethod
    def assess_risk(
        self, traj, targets=None, force_instances=False, show_progress=False
    ):
        pass

    @abstractmethod
    def _match(self, single_traj, instance):
        pass


class LocationAttack(Attack):
    def __init__(self, knowledge_length):
        super(LocationAttack, self).__init__(knowledge_length)

    def assess_risk(
        self, traj: Trajectory, targets=None, force_instances=False, show_progress=False
    ):
        traj = traj.gdf.sort_values(by=[constants.UID, traj.gdf.index.name])
        return self._all_risks(traj, targets, force_instances, show_progress)

    def _match(self, single_traj, instance):
        locs = (
            single_traj.groupby([constants.LATITUDE, constants.LONGITUDE])
            .size()
            .reset_index(name=constants.COUNT)
        )
        inst = pd.DataFrame(data=instance, columns=single_traj.columns)
        inst = inst.astype(dtype=dict(single_traj.dtypes))
        inst = (
            inst.groupby([constants.LATITUDE, constants.LONGITUDE])
            .size()
            .reset_index(name=constants.COUNT + "inst")
        )
        locs_inst = pd.merge(
            locs,
            inst,
            left_on=[constants.LATITUDE, constants.LONGITUDE],
            right_on=[constants.LATITUDE, constants.LONGITUDE],
        )
        if len(locs_inst.index) != len(inst.index):
            return 0
        else:
            condition = (
                locs_inst[constants.COUNT] >= locs_inst[constants.COUNT + "inst"]
            )
            if len(locs_inst[condition].index) != len(inst.index):
                return 0
            else:
                return 1


def frequency_vector(trajectory):
    freq = (
        trajectory.groupby([constants.UID, constants.LATITUDE, constants.LONGITUDE])
        .size()
        .reset_index(name=constants.FREQUENCY)
    )
    return freq.sort_values(by=[constants.UID, constants.FREQUENCY])


class HomeWorkAttack(Attack):
    def __init__(self, knowledge_length=1):
        super(HomeWorkAttack, self).__init__(knowledge_length)

    def _generate_instances(self, single_traj):
        return [single_traj[:2].values]

    def assess_risk(
        self, traj, targets=None, force_instances=False, show_progress=False
    ):
        freq = frequency_vector(traj.gdf)
        return self._all_risks(freq, targets, force_instances, show_progress)

    def _match(self, single_traj, instance):
        inst = pd.DataFrame(data=instance, columns=single_traj.columns)
        locs_inst = pd.merge(
            single_traj[:2],
            inst,
            left_on=[constants.LATITUDE, constants.LONGITUDE],
            right_on=[constants.LATITUDE, constants.LONGITUDE],
        )
        if len(locs_inst.index) == len(inst.index):
            return 1
        else:
            return 0
