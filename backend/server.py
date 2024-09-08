import asyncio
import websockets
import json
from websockets.server import WebSocketServerProtocol

from modules.ground_control import GroundControl
from modules.commands_processor import CommandProcessor


def run_coroutine_in_loop(coroutine: asyncio.Future, loop:asyncio.AbstractEventLoop)->None:
    asyncio.run_coroutine_threadsafe(coroutine, loop)


async def websocket_handler(websocket: WebSocketServerProtocol, command_processor:CommandProcessor,message_queue:asyncio.Queue):
    async def send_messages_from_queue():
        while True:
            try:
                message = await message_queue.get()
                await websocket.send(json.dumps(message))
            except websockets.ConnectionClosed:
                break
            except Exception as e:
                exception_message = str(e)
                print(f"Error sending message: {exception_message}")


    send_task = asyncio.create_task(send_messages_from_queue())
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                command = data.get("command")
                payload = data.get("data")
                response = await command_processor.process_command(command, payload)
            except Exception as e:
                response = {"status": "error", "message": str(e)}
            await websocket.send(json.dumps(response))
    finally:
        send_task.cancel()

async def main():
   
    message_queue = asyncio.Queue()
    gc = GroundControl(message_queue)
    command_processor = CommandProcessor(gc, message_queue)

    loop = asyncio.get_running_loop()
    gc.set_event_loop(loop)

    print(f"Starting server at ws://backend:8765")
    async with websockets.serve(lambda ws: websocket_handler(ws, command_processor,message_queue), "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())