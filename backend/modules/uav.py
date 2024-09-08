import threading
from shapely.geometry import Polygon
from typing import Union

from utils.geo_utils import generate_waypoints

class UAV:
    """
    A class to represent an Unmanned Aerial Vehicle (UAV).

    Attributes:
        uav_id (int): The ID of the UAV.
        buffer_polygon (object): The buffer polygon for the UAV.
        _internal_uav_coordinates (tuple[float, float, float]): The internal coordinates of the UAV.
        observers (list[object]): The list of observers registered to the UAV.
        interpolation_distance (int): The distance for interpolation.
        waypoints (list[tuple[float, float]]): The list of waypoints for the UAV.
        used_waypoints (list[tuple[float, float]]): The list of used waypoints.
        update_cycle (int): The update cycle counter.
        _stop_event (threading.Event): The event to stop the UAV's movement.
    """
    def __init__(self, uav_id:int, buffer_polygon:Polygon,uav_coordinates:tuple[float,float,float],interpolation_distance:int=250):
        self.uav_id:int = uav_id
        self.buffer_polygon:Polygon = buffer_polygon
        self._internal_uav_coordinates:tuple[float,float,float] = uav_coordinates 
        self.init_uav_coordinates:tuple[float,float,float] = uav_coordinates
        self.observers:list[object] = []
        self.interpolation_distance:int = interpolation_distance
        self.waypoints:list[tuple[float,float,float]] = generate_waypoints(self.buffer_polygon, uav_coordinates[:2], self.interpolation_distance)
        self.update_cycle:int=0
        self._stop_event:threading.Event = threading.Event()
        self.start_moving()
        

    @property
    def _uav_coordinates(self)->tuple[float,float,float]:
        return self._internal_uav_coordinates

    @_uav_coordinates.setter
    def _uav_coordinates(self, value:Union[tuple[float,float,float],tuple[float,float]])->None:
        if len(value) == 2:
            value = (*value, 0)
        self._internal_uav_coordinates = value
        self.notify_observers()

    def register_observer(self, observer:object)->None:
        self.observers.append(observer)

    def notify_observers(self)->None:
        for observer in self.observers:
            observer.update({'id':self.uav_id, 'uav_coordinates':self._uav_coordinates})

    def interpolate_next_position(self)->tuple[float,float,float]:
        if (self.update_cycle > -1):
            if not self.waypoints:
                print(f"UAV {self.uav_id} has no waypoints left.")
                self.waypoints = generate_waypoints(self.buffer_polygon, self.init_uav_coordinates[:2], self.interpolation_distance)
                return self._uav_coordinates

            next_waypoint = self.waypoints.pop(0)
            self._uav_coordinates = [next_waypoint[0], next_waypoint[1], 500]
            print(f"UAV {self.uav_id} moved to new position: {next_waypoint}")
            self.update_cycle+=1
            return self._uav_coordinates
        else:
            self.update_cycle+=1
            return self._uav_coordinates
        
    def start_moving(self)->None:
        def move():
            while not self._stop_event.is_set():
                self.interpolate_next_position()
                self._stop_event.wait(2)
        self._thread = threading.Thread(target=move)
        self._thread.start()

    def stop_moving(self)->None:
        if self._thread is not None:
            self._stop_event.set()
            self._thread.join()
            self._thread = None
     
    def to_dict(self)->dict[str,Union[str,float]]:
        return {'id': self.uav_id, 'uav_coordinates': self._uav_coordinates}