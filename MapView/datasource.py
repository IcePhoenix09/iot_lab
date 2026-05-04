import asyncio
import json
from datetime import datetime
import websockets
from kivy import Logger
from pydantic import BaseModel, field_validator
from config import STORE_HOST, STORE_PORT


# Pydantic models
class ProcessedAgentData(BaseModel):
    road_state: str
    user_id: int
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime

    @classmethod
    @field_validator("timestamp", mode="before")
    def check_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            )


class Datasource:
    def __init__(self, user_id: int):
        self.index = 0
        self.user_id = user_id
        self.connection_status = None
        self._new_points = []
        self._task = asyncio.ensure_future(self.connect_to_server())

    def get_new_points(self):
        Logger.debug(self._new_points)
        points = self._new_points
        self._new_points = []
        return points

    async def connect_to_server(self):
        uri = f"ws://{STORE_HOST}:{STORE_PORT}/ws/{self.user_id}"
        while True:
            Logger.info(f"WebSocket: З'єднуємось з {uri} ...")
            try:
                async with websockets.connect(uri) as websocket:
                    self.connection_status = "Connected"
                    Logger.info("WebSocket: УСПІШНО ПІДКЛЮЧЕНО!")
                    try:
                        while True:
                            try:
                                # Чекаємо дані 1 секунду, якщо немає - відпускаємо цикл і перевіряємо знову
                                data = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                                Logger.info(f"WebSocket: ОТРИМАНО ДАНІ: {data}")
                                parsed_data = json.loads(data)
                                if isinstance(parsed_data, str):
                                    parsed_data = json.loads(parsed_data)
                                self.handle_received_data(parsed_data)
                            except asyncio.TimeoutError:
                                await asyncio.sleep(0.01)
                                continue
                    except Exception as e:
                        Logger.error(f"WebSocket: Помилка під час читання: {e}")
            except Exception as e:
                self.connection_status = "Disconnected"
                Logger.error(f"WebSocket: Помилка підключення: {e}")
            
            Logger.info("WebSocket: Повторна спроба через 2 секунди...")
            await asyncio.sleep(2)

    def handle_received_data(self, data):
        # Update your UI or perform actions with received data here
        Logger.debug(f"Received data: {data}")
        
        if isinstance(data, dict):
            data = [data]
            
        try:
            processed_agent_data_list = sorted(
                [
                    ProcessedAgentData(
                        road_state=item.get("road_state", "normal"),
                        user_id=item["agent_data"]["user_id"],
                        x=item["agent_data"]["accelerometer"]["x"],
                        y=item["agent_data"]["accelerometer"]["y"],
                        z=item["agent_data"]["accelerometer"]["z"],
                        latitude=item["agent_data"]["gps"]["latitude"],
                        longitude=item["agent_data"]["gps"]["longitude"],
                        timestamp=item["agent_data"]["timestamp"],
                    )
                    for item in data
                ],
                key=lambda v: v.timestamp,
            )
            new_points = [
                (
                    processed_agent_data.latitude,
                    processed_agent_data.longitude,
                    processed_agent_data.road_state,
                )
                for processed_agent_data in processed_agent_data_list
            ]
            self._new_points.extend(new_points)
        except Exception as e:
            Logger.error(f"Error parsing received data: {e}")
