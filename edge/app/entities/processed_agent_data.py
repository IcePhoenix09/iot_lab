from pydantic import BaseModel
from app.entities.agent_data import AgentData


class ProcessedAgentData(BaseModel):
    road_state: str
    state_code: int
    agent_data: AgentData
