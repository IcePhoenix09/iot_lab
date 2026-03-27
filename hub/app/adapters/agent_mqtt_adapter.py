import logging
import paho.mqtt.client as mqtt
from typing import List
from redis import Redis

from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_gateway import StoreGateway


class AgentMQTTAdapter:
    def __init__(
        self,
        broker_host: str,
        broker_port: int,
        topic: str,
        store_gateway: StoreGateway,
        redis_client: Redis,
        batch_size: int,
    ):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic
        self.store_gateway = store_gateway
        self.redis_client = redis_client
        self.batch_size = batch_size

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info(f"Connected to MQTT broker. Subscribing to topic: {self.topic}")
            client.subscribe(self.topic)
        else:
            logging.error(f"Failed to connect to MQTT broker with code: {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload: str = msg.payload.decode("utf-8")
            # Create ProcessedAgentData instance with the received data
            processed_agent_data = ProcessedAgentData.model_validate_json(
                payload, strict=True
            )

            self.redis_client.lpush(
                "processed_agent_data", processed_agent_data.model_dump_json()
            )
            
            processed_agent_data_batch: List[ProcessedAgentData] = []
            if self.redis_client.llen("processed_agent_data") >= self.batch_size:
                
                # get data from Redis
                for _ in range(self.batch_size):
                    data = ProcessedAgentData.model_validate_json(
                        self.redis_client.lpop("processed_agent_data")
                    )
                    processed_agent_data_batch.append(data)
                
                # sent to Store API
                self.store_gateway.save_data(processed_agent_data_batch=processed_agent_data_batch)
                
        except Exception as e:
            logging.error(f"Error processing MQTT message: {e}")

    def start(self):
        """Connects to the MQTT broker and starts the loop"""
        self.client.connect(self.broker_host, self.broker_port)
        self.client.loop_start()
        logging.info("AgentMQTTAdapter started.")
