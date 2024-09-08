import asyncio
from typing import Union
from modules.swarm import Swarm

class GroundControl:
    """
    A class to manage ground control operations, including handling UAVs and fenced areas.

    Attributes:
        fenced_area (List[List[float]]): The fenced area coordinates.
        is_swarm_init (bool): Flag indicating if the swarm has been initialized.
        message_queue (asyncio.Queue): The message queue for handling responses.
        loop (Optional[asyncio.AbstractEventLoop]): The event loop for asynchronous operations.
        uavs (Optional[List[Dict[str, Union[str, float]]]]): List of UAVs.
        threading_operations (List): List of threading operations.
    """
    def __init__(self, message_queue: asyncio.Queue):
        self.fenced_area:list[list[float]] = []
        self.is_swarm_init:bool = False
        self.message_queue:asyncio.Queue = message_queue
        self.loop:asyncio.AbstractEventLoop = None
        self.uavs:list[dict[str, Union[str, float]]] = None
        self.threading_operations:list = [] 
        
    def add_threading_operation(self, operation:object)->None:
        self.threading_operations.append(operation)

    def stop_operations(self)->None:
        for operation in self.threading_operations:
            operation.stop() 
        self.threading_operations.clear()   
        
    def set_event_loop(self, loop:asyncio.AbstractEventLoop)->None:
        self.loop = loop

    def send_message_to_client(self, message: dict[str, Union[str, dict[str, Union[str, float]]]]) -> None:
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.message_queue.put(message), self.loop)

    def register_swarm(self, swarm:Swarm)->None:
        self.swarm = swarm
        swarm.register_observer(self)

    def update_fenced_area(self, new_area:list[list[float]])->None:
        if not isinstance(new_area, list) or not all(isinstance(point, list) and len(point) == 2 for point in new_area):
            raise ValueError("Fenced area must be a list of coordinate pairs")
        if(new_area[-1]!=new_area[0]):
            new_area.append(new_area[0])
        self.fenced_area = new_area
        if not self.is_swarm_init:
            self.register_swarm(Swarm(self.fenced_area))
            self.is_swarm_init = True
        else:
            self.swarm.update_fenced_area(self.fenced_area)

    def get_swarm_status(self)->dict[str, Union[str, float]]:
        return self.swarm.report_status()

    def send_swarm_status(self,uav_data:dict[str,Union[str,float]])->None:
        message = {
            "message": "UAVs updated",
            "data": uav_data
        }
        self.send_message_to_client(message)

    def update(self, uavs: list[dict[str, Union[str, float]]], uav_data: dict[str, Union[str, float]]) -> None:
        self.uavs = uavs
        self.send_swarm_status(uav_data)
    
    def to_dict(self)->dict[str, Union[str, float]]:
        return {
            'fenced_area': self.fenced_area,
            'is_swarm_init': self.is_swarm_init,
            'swarm': self.swarm.to_dict() if self.swarm else None
        }
        
    def __repr__(self):
        return f"GroundControl(swarm={self.swarm})"