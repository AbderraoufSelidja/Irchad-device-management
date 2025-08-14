from fastapi import WebSocket, WebSocketDisconnect
from typing import Set
from schemas import DeviceStatusUpdate
import json

class WebSocketManager:
    def __init__(self):
        self.outgoing_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.outgoing_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.outgoing_connections.discard(websocket) 

    async def broadcast_device_status(self, message: DeviceStatusUpdate):
        disconnected = []

        for websocket in self.outgoing_connections:
            try:
                await websocket.send_json(json.loads(message.json()))
            except WebSocketDisconnect:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.outgoing_connections.discard(websocket)


# import fastapi
# from fastapi import WebSocket, WebSocketDisconnect
# from jose import JWTError, jwt
# from sqlalchemy.orm import Session
# from typing import Dict
# from db.models.devices import User, Occupation
# from schemas import DeviceStatusUpdate
# import json

# # Configuration JWT
# SECRET_KEY = "secret_key"
# ALGORITHM = "HS256"

# class WebSocketUser:
#     def __init__(self, websocket: WebSocket, user_id: int, role: str):
#         self.websocket = websocket
#         self.user_id = user_id
#         self.role = role


# class WebSocketManagerSecure:
#     def __init__(self):
#         self.outgoing_connections: Dict[int, WebSocketUser] = {}

#     async def connect(self, websocket: WebSocket):
#         token = websocket.query_params.get("token")
#         if not token:
#             await websocket.close(code=1008)
#             return
#         try:
#             payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#             user_id = int(payload.get("user_id"))
#             role = payload.get("role")
#         except (JWTError, ValueError):
#             await websocket.close(code=1008)
#             return
        
#         await websocket.accept()
#         self.outgoing_connections[id(websocket)] = WebSocketUser(websocket, user_id, role)

#     def disconnect(self, websocket: WebSocket):
#         self.outgoing_connections.pop(id(websocket), None)

#     async def broadcast_device_status(self, message: DeviceStatusUpdate, db: Session):
#         disconnected = []

#         for conn_id, ws_user in self.outgoing_connections.items():
#             websocket = ws_user.websocket
#             try:
#                 if await self._can_receive(ws_user, message.serial_number, db):
#                     await websocket.send_json(json.loads(message.json()))
#             except WebSocketDisconnect:
#                 disconnected.append(conn_id)

#         for conn_id in disconnected:
#             self.outgoing_connections.pop(conn_id, None)

#     async def _can_receive(self, ws_user: WebSocketUser, serial_number: int, db: Session) -> bool:
#         if ws_user.role == "admin":
#             return True
#         if ws_user.role == "maintenancier":
#             occupation_exists = db.query(Occupation).filter(
#                 Occupation.user_id == ws_user.user_id,
#                 Occupation.device_serial_number == str(serial_number),
#                 Occupation.occupied == True
#             ).first()
#             return occupation_exists is not None

#         return False

    # from enum import Enum
    # from pydantic import BaseModel, ValidationError
    # from fastapi import APIRouter, WebSocket, WebSocketDisconnect
    # from websockets.exceptions import ConnectionClosed
    # from db.models.devices import OperationalStatusEnum, ConnectionStatusEnum

    # class WebSocketManager:
    #     """
    #     Manages WebSocket connections for incoming and outgoing messages.
    #     """

    #     def __init__(self):
    #         """
    #         Initializes WebSocket connection sets for incoming and outgoing connections.
    #         """

    #         self.incoming_connections: set[WebSocket] = set()
    #         self.outgoing_connections: set[WebSocket] = set()

    #     async def connect_incoming(self, websocket: WebSocket):
    #         """
    #         Accepts and registers an incoming WebSocket connection.
    #         """

    #         await websocket.accept()
    #         self.incoming_connections.add(websocket)

    #     async def connect_outgoing(self, websocket: WebSocket):
    #         """
    #         Accepts and registers an outgoing WebSocket connection.
    #         """

    #         await websocket.accept()
    #         self.outgoing_connections.add(websocket)

    #     def disconnect_incoming(self, websocket: WebSocket):
    #         """
    #         Removes an incoming WebSocket connection.
    #         """

    #         self.incoming_connections.discard(websocket)

    #     def disconnect_outgoing(self, websocket: WebSocket):
    #         """
    #         Removes an outgoing WebSocket connection.
    #         """

    #         self.outgoing_connections.discard(websocket)

    #     async def send(self, websocket: WebSocket, message: dict):
    #         """
    #         Sends a JSON message to a specific WebSocket connection.
    #         """

    #         await websocket.send_json(message)

    #     async def send_to_all_incoming(self, message: dict):
    #         """
    #         Broadcasts a message to all incoming WebSocket connections.
    #         Disconnects any unresponsive clients.
    #         """

    #         disconnected = set()
    #         for connection in self.incoming_connections:
    #             try:
    #                 await self.send(connection, message)
    #             except (WebSocketDisconnect, ConnectionClosed, RuntimeError):
    #                 disconnected.add(connection)

    #         for connection in disconnected:
    #             self.incoming_connections.remove(connection)

    #     async def send_to_all_outgoing(self, message: dict):
    #         """
    #         Broadcasts a message to all outgoing WebSocket connections.
    #         Disconnects any unresponsive clients.
    #         """

    #         disconnected = set()
    #         for connection in self.outgoing_connections:
    #             try:
    #                 await self.send(connection, message)
    #             except (WebSocketDisconnect, ConnectionClosed, RuntimeError):
    #                 disconnected.add(connection)

    #         for connection in disconnected:
    #             self.outgoing_connections.remove(connection)

    #     async def receive_and_forward(self, websocket: WebSocket):
    #         """
    #         Receives a message from an incoming WebSocket and forwards it to all outgoing connections.
    #         Checks if the message type is correct before forwarding.
    #         Disconnects the WebSocket if it gets disconnected.
    #         """

    #         try:
    #             message = await websocket.receive_json()
    #         except WebSocketDisconnect:
    #             if websocket in self.incoming_connections:
    #                 self.disconnect_incoming(websocket)
    #             elif websocket in self.outgoing_connections:
    #                 self.disconnect_outgoing(websocket)
    #             return

    #         try:
    #             validated_message = BatteryLevelMessage.model_validate(message)
    #         except ValidationError:
    #             try:
    #                 validated_message = OperationalStatusMessage.model_validate(message)
    #             except ValidationError:
    #                 try:
    #                     validated_message = ConnectionStatusMessage.model_validate(message)
    #                 except ValidationError:
    #                     await websocket.send_json({"error": "Invalid websocket message"})
    #                     return

    #         await self.send_to_all_outgoing(validated_message.model_dump())


    # router = APIRouter()
    # manager = WebSocketManager()


    # @router.websocket("/ws/incoming")
    # async def incoming_websocket_endpoint(websocket: WebSocket):
    #     """
    #     WebSocket endpoint for handling incoming messages.
    #     """

    #     await manager.connect_incoming(websocket)
    #     try:
    #         while True:
    #             await manager.receive_and_forward(websocket)
    #     except WebSocketDisconnect:
    #         manager.disconnect_incoming(websocket)


    # @router.websocket("/ws/outgoing")
    # async def outgoing_websocket_endpoint(websocket: WebSocket):
    #     """
    #     WebSocket endpoint for handling outgoing messages.
    #     """

    #     await manager.connect_outgoing(websocket)
    #     try:
    #         while True:
    #             await websocket.receive_json()
    #     except WebSocketDisconnect:
    #         manager.disconnect_outgoing(websocket)
