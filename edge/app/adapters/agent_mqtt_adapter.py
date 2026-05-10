import logging
import paho.mqtt.client as mqtt
from app.interfaces.agent_gateway import AgentGateway
from app.entities.agent_data import AgentData
from app.entities.parking_data import ParkingData  # Import the new parking model
from app.usecases.data_processing import process_agent_data
from app.interfaces.hub_gateway import HubGateway


class AgentMQTTAdapter(AgentGateway):
    def __init__(
        self,
        broker_host,
        broker_port,
        topic,
        hub_gateway: HubGateway,
        parking_topic="parking_data_topic",
        batch_size=10,
    ):
        self.batch_size = batch_size
        # MQTT
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic
        self.parking_topic = parking_topic
        self.client = mqtt.Client()
        # Hub
        self.hub_gateway = hub_gateway

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT broker")
            self.client.subscribe(self.topic)
            self.client.subscribe(self.parking_topic)
        else:
            logging.info(f"Failed to connect to MQTT broker with code: {rc}")

    def on_message(self, client, userdata, msg):
        """Processing agent data and sent it to hub gateway"""
        try:
            payload: str = msg.payload.decode("utf-8")
            
            # Route based on the topic the message arrived on
            if msg.topic == self.topic:
                # Create AgentData instance with the received data
                agent_data = AgentData.model_validate_json(payload, strict=True)
                # Process the received data
                processed_data = process_agent_data(agent_data)
                # Store the agent_data in the database
                if not self.hub_gateway.save_data(processed_data):
                    logging.error("Hub is not available (Road Data)")
                    
            elif msg.topic == self.parking_topic:
                # Create ParkingData instance with the received data
                parking_data = ParkingData.model_validate_json(payload, strict=True)
                # Pass directly to hub gateway (no road state processing needed)
                if not self.hub_gateway.save_parking_data(parking_data):
                    logging.error("Hub is not available (Parking Data)")
                    
        except Exception as e:
            logging.info(f"Error processing MQTT message on topic {msg.topic}: {e}")

    def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_host, self.broker_port, 60)

    def start(self):
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()


# Usage example:
if __name__ == "__main__":
    broker_host = "localhost"
    broker_port = 1883
    topic = "agent_data_topic"
    parking_topic = "parking_data_topic"

    store_gateway = HubGateway()
    adapter = AgentMQTTAdapter(broker_host, broker_port, topic, store_gateway, parking_topic=parking_topic)
    adapter.connect()
    adapter.start()
    try:
        # Keep the adapter running in the background
        while True:
            pass
    except KeyboardInterrupt:
        adapter.stop()
        logging.info("Adapter stopped.")