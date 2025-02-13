# (Singleton Pattern)
from pyproj import Proj


class _Constants:
    def __init__(self):
        self.R = 6371000  # Radius of the Earth in meters


class _Projections:
    def __init__(self):
        self.WGS84 = Proj(init="epsg:4326")  # WGS84
        self.WEB_MERCATOR = Proj(init="epsg:3857")  # Web Mercator


class _ColumnNames:
    TRAJECTORY_ID = "trajectory_id"
    X = "x"
    Y = "y"
    T = "t"
    PREV_X = "prev_x"
    PREV_Y = "prev_y"
    PREV_T = "prev_t"
    FIRST_X = "first_x"
    FIRST_Y = "first_y"
    FIRST_T = "first_t"
    LAST_X = "last_x"
    LAST_Y = "last_y"
    LAST_T = "last_t"
    TIME_DIFF = "time_diff"
    DISTANCE = "distance"
    STRAIGHT_LINE_DISTANCE = "straight_line_distance"
    SPEED = "speed"
    STOP = "stop"
    SEGMENT_ID = "segment_id"
    OUTLIER = "outlier"
    CLUSTER = "cluster"
    TURNING_ANGLE = "starting_angle"


# Acesso às variáveis globais
projections = _Projections()
col_names = _ColumnNames()
constants = _Constants()
