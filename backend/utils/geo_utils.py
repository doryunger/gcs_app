import pyproj
import numpy as np
from shapely.geometry import Point, Polygon
from shapely.ops import transform

def create_polygon(coords: list[tuple[float, float]]) -> Polygon:
    """
    Create a polygon from a list of coordinates.

    Args:
        coords (List[Tuple[float, float]]): List of (latitude, longitude) tuples.

    Returns:
        Polygon: A Shapely Polygon object.
    """
    polygon = Polygon(coords)
    return polygon
    
   
def interpolate_points_on_polygon(polygon: Polygon, num_points: int) -> list[tuple[float, float, float]]:
    """
    Interpolate points along the perimeter of a polygon.

    Args:
        polygon (Polygon): A Shapely Polygon object.
        num_points (int): Number of points to interpolate.

    Returns:
        List[Tuple[float, float, float]]: List of interpolated points as (latitude, longitude, altitude) tuples.
    """
    perimeter = polygon.length
    distance_between_points = perimeter / num_points
    points = []

    for i in range(num_points):
        point = polygon.exterior.interpolate(i * distance_between_points)
        points.append((point.y, point.x, 500))

    return points

def shrink_polygon(polygon: Polygon, distance: float) -> Polygon:
        """
        Shrink a polygon by a specified distance.

        Args:
            polygon (Polygon): A Shapely Polygon object.
            distance (float): Distance to shrink the polygon.

        Returns:
            Polygon: A new Shapely Polygon object representing the shrunken polygon.
        """
        wgs84 = pyproj.CRS('EPSG:4326')
        utm = pyproj.CRS('EPSG:3857')  
        transformer_to_utm = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True)
        transformer_to_wgs84 = pyproj.Transformer.from_crs(utm, wgs84, always_xy=True)
        projected_polygon = transform(transformer_to_utm.transform, polygon)
        coords = list(projected_polygon.exterior.coords)
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        shrunken_coords = []
        for i in range(len(coords)):
            p1 = np.array(coords[i - 1])
            p2 = np.array(coords[i])
            p3 = np.array(coords[(i + 1) % len(coords)])
            v1 = p1 - p2
            v2 = p3 - p2
            norm_v1 = np.linalg.norm(v1)
            norm_v2 = np.linalg.norm(v2)
            if norm_v1 == 0 or norm_v2 == 0:
                continue
            v1 /= norm_v1
            v2 /= norm_v2
            normal = v1 + v2
            normal /= np.linalg.norm(normal)
            angle = np.arccos(np.clip(np.dot(v1, v2), -1.0, 1.0)) / 2
            inward_distance = distance / np.sin(angle)
            inward_point = p2 + normal * inward_distance
            shrunken_coords.append(tuple(inward_point))
        shrunken_projected_polygon = Polygon(shrunken_coords)
        shrunken_polygon_wgs84 = transform(transformer_to_wgs84.transform, shrunken_projected_polygon)
        return shrunken_polygon_wgs84

def generate_waypoints(buffer_polygon: Polygon, uav_coordinates: tuple[float, float], interpolation_distance: float = 250) -> list[tuple[float, float, float]]:
    """
    Generate waypoints along the perimeter of a buffer polygon.

    Args:
        buffer_polygon (Polygon): A Shapely Polygon object representing the buffer area.
        uav_coordinates (Tuple[float, float]): Current UAV coordinates as (latitude, longitude).
        interpolation_distance (float, optional): Distance between waypoints. Defaults to 250.

    Returns:
        List[Tuple[float, float, float]]: List of waypoints as (latitude, longitude, altitude) tuples.
    """
    wgs84 = pyproj.CRS('EPSG:4326')
    utm = pyproj.CRS('EPSG:3857')
    transformer_to_utm = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True)
    transformer_to_wgs84 = pyproj.Transformer.from_crs(utm, wgs84, always_xy=True)
    projected_polygon = transform(transformer_to_utm.transform, buffer_polygon)
    perimeter_length = projected_polygon.length
    num_waypoints = int(perimeter_length / interpolation_distance)
    current_position = Point(uav_coordinates[1], uav_coordinates[0])
    projected_current_position = transform(transformer_to_utm.transform, current_position)
    start_distance = projected_polygon.exterior.project(projected_current_position)
    waypoints = []
    for i in range(num_waypoints):
        waypoint = projected_polygon.exterior.interpolate(start_distance + i * interpolation_distance)
        waypoint_wgs84 = transform(transformer_to_wgs84.transform, waypoint)
        waypoints.append((waypoint_wgs84.y, waypoint_wgs84.x, 500)) 
    return waypoints
