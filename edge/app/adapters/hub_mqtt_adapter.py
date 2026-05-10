import logging

import requests as requests
from paho.mqtt import client as mqtt_client

from app.entities.processed_agent_data import ProcessedAgentData
from app.entities.parking_data import ParkingData
from app.interfaces.hub_gateway import HubGateway


class HubMqttAdapter(HubGateway):
    def __init__(self, broker, port, topic, parking_topic="parking_data_topic"):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.parking_topic = parking_topic
        self.mqtt_client = self._connect_mqtt(broker, port)

    def save_data(self, processed_data: ProcessedAgentData):
        """
        Save the processed road data to the Hub.
        Parameters:
            processed_data (ProcessedAgentData): Processed road data to be saved.
        Returns:
            bool: True if the data is successfully saved, False otherwise.
        """
        msg = processed_data.model_dump_json()
        result = self.mqtt_client.publish(self.topic, msg)
        status = result[0]
        if status == 0:
            return True
        else:
            print(f"Failed to send message to topic {self.topic}")
            return False

    def save_parking_data(self, parking_data: ParkingData):
        """
        Save the parking data to the Hub.
        Parameters:
            parking_data (ParkingData): Parking data to be saved.
        Returns:
            bool: True if the data is successfully saved, False otherwise.
        """
        # use model_dump_json() to correctly serialize the datetime object
        msg = parking_data.model_dump_json(by_alias=True)
        result = self.mqtt_client.publish(self.parking_topic, msg)
        status = result[0]
        if status == 0:
            return True
        else:
            print(f"Failed to send message to topic {self.parking_topic}")
            return False

    @staticmethod
    def _connect_mqtt(broker, port):
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
