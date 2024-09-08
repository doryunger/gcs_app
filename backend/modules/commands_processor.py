import asyncio
from typing import Union

class CommandProcessor:
    """
    A class to process various commands related to ground control and message queue.

    Attributes:
        ground_control: An instance of the ground control system.
        message_queue: An asyncio queue for handling messages.
    """
    def __init__(self, ground_control:list[list[float,float]],message_queue:asyncio.Queue)->None:
        self.ground_control = ground_control
        self.message_queue = message_queue

    async def process_command(self, command:str, payload:list[list[float,float]]) -> dict[str, Union[str, dict[str, any]]]:
        if command == "update_fenced_area":
            try:
                self.ground_control.update_fenced_area(payload)
                return {"status": "success", "message": "Fenced area updated", "data": self.ground_control.to_dict()}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        elif command == 'send_swarm_status':
            self.ground_control.send_swarm_status()
            response = {"status": "success", "message": "Swarm status sent"}
            await self.message_queue.put(response) 
            return response
        else:
            return {"status": "error", "message": "Unknown command"}