from sklearn.metrics.pairwise import haversine_distances
from shapely.geometry import Point
from math import radians


def haversine(p1: Point, p2: Point, earth_radius_km=6378) -> float:
    p1 = [p1.x, p1.y]
    p2 = [p2.x, p2.y]
    p1_in_radians = [radians(i) for i in p1]
    p2_in_radians = [radians(i) for i in p2]
    result = haversine_distances([p1_in_radians, p2_in_radians])[0][1]
    return result * earth_radius_km


def euclidean(p1: Point, p2: Point):
    return p1.distance(p2)
