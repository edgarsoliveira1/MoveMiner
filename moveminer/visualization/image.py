from moveminer.core.Trajectory import Trajectory
from moveminer.utils import constants
from shapely import LineString
import geopandas as gpd
import contextily as cx

def traj_plot(t:Trajectory, ax=None):
    linestring = t.gdf['geometry'].apply(lambda p: [p.x, p.y])
    linestring = LineString(linestring)
    gdf = gpd.GeoDataFrame(geometry=[linestring])
    ax = gdf.plot(ax=ax)
    return t.gdf.plot(ax=ax)

def plot(t:any, ax=None, attribution=''):
    t_type = type(t)
    if t_type == Trajectory:
        if t.is_multuid:
            t.gdf = t.gdf.sort_values(by=[constants.UID, constants.DATETIME])
        ax = ax if ax else traj_plot(t)
        crs = t.gdf.crs.to_string()
        if not t.geo:
            return ax
    if t_type == list:
        ax = traj_plot(t[0])
        crs = t[0].gdf.crs.to_string()
        legend = [t[0].gdf[constants.UID].unique()[0]]
        for traj in t[1:]:
            ax = traj_plot(traj, ax=ax) 
            legend.append(traj.gdf[constants.UID].unique()[0])
        ax.legend(legend)
        if not t[0].geo:
            return ax
    return cx.add_basemap(
        ax, 
        crs=crs, 
        attribution=attribution
        )