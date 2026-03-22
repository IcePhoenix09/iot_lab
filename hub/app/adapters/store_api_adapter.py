import json
import logging
from typing import List

import pydantic_core
import requests

from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_gateway import StoreGateway


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]):
        """
        Save the processed road data to the Store API.
        Parameters:
            processed_agent_data_batch (dict): Processed road data to be saved.
        Returns:
            bool: True if the data is successfully saved, False otherwise.
        """
        # get json data
        payload = [data.model_dump() for data in processed_agent_data_batch]
        
        # зробити post запит на ‘{store_host}/processed_agent_data’ з списком елементів ProcessedAgentData.
        endpoint = f"{self.api_base_url}/processed_agent_data"
        
        try:
            # send POST request
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            logging.info(f"Success: {len(processed_agent_data_batch)} records saved to Store.")
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred while sending data to Store API: {e}")
            return False
