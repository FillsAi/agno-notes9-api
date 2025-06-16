from enum import Enum
from typing import AsyncGenerator, List, Optional, Generator

from agno.agent import Agent
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agents.operator import AgentType, get_agent, get_available_agents
from utils.log import logger

######################################################
## Router for the Agent Interface
######################################################

agents_router = APIRouter(prefix="/agents", tags=["Agents"])


class Model(str, Enum):
    gpt_4o = "gpt-4o"
    o3_mini = "o3-mini"
    # Add Amazon Nova models for proper support
    nova_lite = "amazon.nova-lite-v1:0"


@agents_router.get("", response_model=List[str])
async def list_agents():
    """
    Returns a list of all available agent IDs.

    Returns:
        List[str]: List of agent identifiers
    """
    return get_available_agents()


async def chat_response_streamer(agent: Agent, message: str) -> AsyncGenerator:
    """
    Stream agent responses chunk by chunk using synchronous streaming.
    
    This implementation avoids async issues with AWS Bedrock by using
    the synchronous streaming approach that works reliably.

    Args:
        agent: The agent instance to interact with
        message: User message to process

    Yields:
        Text chunks from the agent response
    """
    # Use synchronous streaming (this avoids the async warning!)
    run_response = agent.run(message, stream=True)
    
    # Iterate through the synchronous stream
    for chunk in run_response:
        # chunk.content contains the text response from the Agent
        if chunk.content:
            yield chunk.content


class RunRequest(BaseModel):
    """Request model for running an agent"""

    message: str
    stream: bool = False  # Default to non-streaming for reliability
    model: Model = Model.nova_lite  # Default to Amazon Nova Lite (works with AWS Bedrock)
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@agents_router.post("/{agent_id}/runs", status_code=status.HTTP_200_OK)
async def run_agent(agent_id: AgentType, body: RunRequest):
    """
    Sends a message to a specific agent and returns the response.

    Args:
        agent_id: The ID of the agent to interact with
        body: Request parameters including the message

    Returns:
        Either a streaming response or the complete agent response
    """
    logger.debug(f"RunRequest: {body}")

    try:
        agent: Agent = get_agent(
            model_id=body.model.value,
            agent_id=agent_id,
            user_id=body.user_id,
            session_id=body.session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent not found: {str(e)}")

    if body.stream:
        return StreamingResponse(
            chat_response_streamer(agent, body.message),
            media_type="text/event-stream",
        )
    else:
        # Use synchronous run for reliability
        response = agent.run(body.message, stream=False)
        return {"content": response.content if response.content else "No response generated"}
