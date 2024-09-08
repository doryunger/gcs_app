import pytest
import asyncio
import json
import websockets
from modules.ground_control import GroundControl
from modules.commands_processor import CommandProcessor
from server import websocket_handler

@pytest.mark.asyncio
async def test_websocket_handler():
    gc = GroundControl()  # Initialize the ground control instance
    command_processor = CommandProcessor(gc)  # Pass it to the CommandProcessor

    async def mock_server(websocket):
        await websocket_handler(websocket, command_processor)

    # Start the mock server
    server = await websockets.serve(mock_server, "localhost", 8765)

    async with websockets.connect("ws://localhost:8765") as websocket:
        # Send a test command with a polygon
        command = {
            "command": "update_fenced_area",
            "data": [[0, 0], [10, 0], [10, 10], [0, 10]]
        }
        await websocket.send(json.dumps(command))

        # Receive response
        response = await websocket.recv()
        response_data = json.loads(response)

        # Assert the response
        assert response_data["status"] == "success"
        assert response_data["message"] == "Fenced area updated"

    server.close()
    await server.wait_closed()