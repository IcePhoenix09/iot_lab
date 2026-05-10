from paho.mqtt import client as mqtt_client
import json
import time
from schemas import AggregatedDataSchema, ParkingSchema, TrafficLightSchema
from file_datasource import FileDatasource
import config


def connect_mqtt(broker, port):
    """Create MQTT client"""
    print(f"CONNECT TO {broker}:{port}")

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT Broker ({broker}:{port})!")
        else:
            print("Failed to connect {broker}:{port}, return code %d\n", rc)
            exit(rc)  # Stop execution

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()
    return client


def publish(client, topic, datasource, delay):
    datasource.startReading()
    road_schema = AggregatedDataSchema()
    parking_schema = ParkingSchema()
    traffic_light_schema = TrafficLightSchema()

    while True:
        time.sleep(delay)
        road_data, parking_data, traffic_light_data = datasource.read()
        
        msg_road = road_schema.dumps(road_data)
        result_road = client.publish(topic, msg_road)
        
        msg_parking = parking_schema.dumps(parking_data)
        result_parking = client.publish("parking_data_topic", msg_parking)

        msg_traffic_light = traffic_light_schema.dumps(traffic_light_data)
        result_traffic_light = client.publish("traffic_light_data_topic", msg_traffic_light)

        if result_road[0] == 0 and result_parking[0] == 0 and result_traffic_light[0] == 0:
            pass
            # print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")


def run():
    # Prepare mqtt client
    client = connect_mqtt(config.MQTT_BROKER_HOST, config.MQTT_BROKER_PORT)
    # Prepare datasource
    datasource = FileDatasource(
        config.USER_ID,
        "data/accelerometer.csv", 
        "data/gps.csv", 
        "data/parking.csv",
        "data/traffic_light.csv"
    )
    # Infinity publish data
    publish(client, config.MQTT_TOPIC, datasource, config.DELAY)


if __name__ == "__main__":
    run()
