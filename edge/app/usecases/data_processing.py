from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData


def process_agent_data(
    agent_data: AgentData,
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data that containing accelerometer, GPS, and timestamp.
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state of the road surface and agent data.
    """
    # I will use the z coordinate of the accelerometer to classify the state of the road surface.
    z_value = agent_data.accelerometer.z

    # This is a very simple classification based on the z value of the accelerometer. 
    # In futere we can change it to more sophisticated method, such as machine learning, to classify the state of the road surface.
    if z_value < -5.0:
        road_state = "hole"
    elif z_value > 5.0:
        road_state = "bump"
    else:
        road_state = "normal"

    return ProcessedAgentData(
        road_state=road_state,
        agent_data=agent_data
    )

