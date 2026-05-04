import requests
import time
from datetime import datetime, timezone

url = "http://127.0.0.1:8000/processed_agent_data/"

def send_mock_data(lat, lon, state):
    data = [{
        "road_state": state,
        "agent_data": {
            "user_id": 1,
            "accelerometer": {"x": 0.0, "y": 0.0, "z": 0.0},
            "gps": {"latitude": lat, "longitude": lon},
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }]
    r = requests.post(url, json=data)
    print(f"Відправлено: {lat}, {lon}, Статус дороги: {state} | Статус запиту: {r.status_code}")

# Координати маршруту у центрі Києва
points = [
    (50.4501, 30.5234, "normal"),
    (50.4503, 30.5238, "pothole"),
    (50.4505, 30.5242, "normal"),
    (50.4508, 30.5248, "bump")
]

while True:
    for p in points:
        send_mock_data(*p)
        time.sleep(2)
