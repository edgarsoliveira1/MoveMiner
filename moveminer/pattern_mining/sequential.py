from moveminer.core.Trajectory import Trajectory
from moveminer.utils import constants

def cluster_sequences(traj: Trajectory):
    if not constants.CLUSTER in traj.gdf.columns:
        return [], []
    traj_gdf = traj.gdf
    uids = []
    seqs = []

    for uid in traj_gdf[constants.UID].unique():
        traj_gdf_uid = traj_gdf[traj_gdf[constants.UID] == uid]
        clusters_serie = traj_gdf_uid[constants.CLUSTER]
        p = clusters_serie[0]
        traj_seq = [p]
        for c in clusters_serie[1:]:
            if p != c:
                traj_seq.append(c)
            p = c
        uids.append(uid)
        seqs.append(traj_seq)
    return uids, seqs

from typing import List

class PrefixSpan:
    def __init__(self, min_sup=2) -> None:
        self.min_sup = min_sup

    def prefix_span(self, prefix:List[any], S:List[List[any]]):
        # count items
        count = {}
        for s in S:
            for i in range(len(s)):
                if s[i] not in count:
                    count[s[i]] = 1
                else:
                    count[s[i]] += 1
        # remove infrequent items
        L = [(k, v) for k, v in count.items() if v >= self.min_sup]
        # for each frequent item, make a project e call prefix again
        for (a, v) in sorted(L, key=lambda x: x[1], reverse=True):
            yield (prefix + [a], v)
            _S = self._project(S, a)
            if _S:
                yield from self.prefix_span(prefix + [a], _S)
        
    def _project(self, S, a):
        _S = []
        for s in S:
            for i in range(len(s)):
                if s[i] == a:
                    _S.append(s[i + 1:])
                    break
        return _S

# # Test input:
# sequences = [
#     ['a', 'c', 'a'],
#     ['b', 'c', 'a'],
#     ['a', 'b', 'c'],
#     ['b', 'c', 'd'],
#     ['b', 'a', 'c'],
#     ['b', 'b', 'c'],
# ]
# min_sup = 3
# # expected result:
# example_result =[
#     (['c'], 6),
#     (['b'], 6),
#     (['b', 'c'], 5),
#     (['a'], 5),
#     (['a', 'c'], 3),
# ]