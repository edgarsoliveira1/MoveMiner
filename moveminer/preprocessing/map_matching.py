from ..core.Trajectory import Trajectory
import osmnx
from moveminer.core.Trajectory import Trajectory
from moveminer.utils import constants
import osmnx

def map_matching(t:Trajectory, network_type='all'):
    traj = t.copy()
    gdf = traj.gdf
    bounds = gdf.total_bounds
    graph = osmnx.graph_from_bbox(bounds[1], bounds[3], bounds[0], bounds[2], network_type=network_type)
    nearest_edges = osmnx.nearest_edges(graph, gdf[constants.GEOMETRY].x, gdf[constants.GEOMETRY].y)
    gdf_edges = osmnx.graph_to_gdfs(graph, nodes=False)
    # find the closest point, inside the line, to move the external point
    geometries = gdf[constants.GEOMETRY]
    for i in range(len(nearest_edges)):
        e = nearest_edges[i]
        df_edges = gdf_edges[
            (gdf_edges.index.get_level_values('u') == e[0])
            & (gdf_edges.index.get_level_values('v') == e[1])
        ]
        line = df_edges[constants.GEOMETRY]
        nearest_point = line.interpolate(line.project(geometries[i]))
        gdf[constants.GEOMETRY][i] = nearest_point.values[0]
    return traj