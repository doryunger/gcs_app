from typing import Union

from modules.uav import UAV
from utils.geo_utils import shrink_polygon, create_polygon, interpolate_points_on_polygon

class Swarm:
    """
        A class to manage a swarm of UAVs within a fenced area.

        Attributes:
            fenced_area (list[tuple[float, float]]): The coordinates of the fenced area.
            fenced_area_polygon (Polygon): The polygon representation of the fenced area.
            buffer_polygon (Polygon): The shrunken polygon used for UAV positioning.
            num_uavs (int): The number of UAVs in the swarm.
            uavs (list[UAV]): The list of UAVs in the swarm.
            observers (list): The list of observers registered to the swarm.
    """
    def __init__(self, fenced_area, num_uavs=6):
        self.fenced_area:list[tuple[float,float]] = fenced_area
        self.fenced_area_polygon = create_polygon(fenced_area)
        self.buffer_polygon = shrink_polygon(self.fenced_area_polygon, 250)  
        self.num_uavs:int = num_uavs
        self.uavs:list[UAV] = self.initialize_uavs()
        self.observers:list = []

    def initialize_uavs(self)->list[UAV]:
        uav_positions = interpolate_points_on_polygon(self.buffer_polygon, self.num_uavs)
        uavs = []
        for i, pos in enumerate(uav_positions):
            uav = UAV(uav_id=i+1, buffer_polygon=self.buffer_polygon, uav_coordinates=pos)
            if uav:
                uav.register_observer(self)
                uavs.append(uav)
        return uavs

    def update(self,data: dict[str,Union[str,float]])->None:
        self.notify_observers(data)

    def register_observer(self, observer:object)->None:
        self.observers.append(observer)

    def notify_observers(self,uav_data:list[dict[str,Union[str,float]]])->None:
        for observer in self.observers:
            observer.update(self.uavs,uav_data)
            
    def to_dict(self)->dict[str,Union[str,float]]:
        return {'uavs': [uav.to_dict() for uav in self.uavs]}

    def reinitialize_swarm(self, new_fenced_area:list[tuple[float,float]])->None:
        for uav in self.uavs:
            uav.stop_moving()
        self.uavs = []

        self.fenced_area = new_fenced_area
        self.fenced_area_polygon = create_polygon(new_fenced_area)
        self.buffer_polygon  = shrink_polygon(self.fenced_area_polygon, 250) 
        self.uavs = self.initialize_uavs()

    def update_fenced_area(self, new_fenced_area:list[tuple[float,float]])->None:
        self.reinitialize_swarm(new_fenced_area)
    
