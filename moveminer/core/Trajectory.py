from pandas.core.indexes.datetimes import DatetimeIndex
from shapely.geometry import Point
from moveminer.utils import distance_metrics
from moveminer.utils import constants
from geopandas import GeoDataFrame
from pandas import DataFrame, to_datetime

class Trajectory:
    def __init__(
        self,
        df: GeoDataFrame | DataFrame,
        x=constants.LATITUDE,
        y=constants.LONGITUDE,
        t=constants.DATETIME,
        geo=True,
        crs="WGS84",
        uid=constants.UID
    ):
        if len(df) < 2:
            raise ValueError("A Trajectory must have 2 or more points.")
        
        if not isinstance(df, GeoDataFrame):
            if x is None or y is None:
                raise ValueError("You must to specify the 'x' end 'y' columns")
            df = GeoDataFrame(
                    df,
                    crs=crs,
                    geometry=[Point(xy) for xy in zip(df[x], df[y])],
                )
            df[constants.LATITUDE] = df[x]
            df[constants.LONGITUDE] = df[y]
            if x != constants.LATITUDE:
                df.drop(columns=[x], inplace=True)
            if y != constants.LONGITUDE:
                df.drop(columns=[y], inplace=True)
        
        if not isinstance(df.index, DatetimeIndex):
            if y is None:
                raise ValueError("You must to specify the 't' column")
            df[constants.DATETIME] = to_datetime(df[t])
            df[constants.COUNT] = df.index
            df = df.set_index(t)
        
        if df.index.tzinfo is not None:
            df = df.tz_localize(None)
        
        df = df.tz_localize(None)
        # Remove duplicated index to prevent errors
        # self.gdf = df[~df.index.duplicated(keep="first")]
        self.gdf = df
        # Flag if latitude and longitude
        self.geo = geo
        self.is_multuid = False
        if uid in df.columns:
            self.gdf[constants.UID] = self.gdf[uid]
            if uid != constants.UID:
                self.gdf.drop(columns=[uid], inplace=True)
            if len(self.gdf[constants.UID].unique()) > 1:
                self.is_multuid = True
                self.gdf = self.gdf.sort_values(by=[constants.UID, constants.DATETIME])
        # Set the right distance metric
        self.distance = distance_metrics.euclidean
        if geo:
            self.distance = distance_metrics.haversine
    
    def __str__(self):
        return self.gdf.__str__()
    
    def get_uid(self, uid):
        return Trajectory(
            self.gdf[self.gdf[constants.UID] == uid].copy(),
            geo=self.geo,
        )
    
    def copy(self):
        return Trajectory(
            self.gdf.copy(),
            geo=self.geo,
        )
