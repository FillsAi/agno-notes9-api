from textwrap import dedent
from typing import Optional
import boto3

from agno.agent import Agent, AgentKnowledge
from agno.models.aws import AwsBedrock
from agno.memory.agent import AgentMemory
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.vectordb.pgvector import PgVector, SearchType

from agents.settings import agent_settings
from db.session import db_url


def get_sage(
    model_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Agent:
    """
    Create a Sage agent with AWS Bedrock using the proven working pattern.
    
    This implementation uses explicit boto3 client configuration to avoid 
    async streaming issues and runtime warnings.
    """
    
    # Use Amazon Nova Lite v1:0 as default model
    model_id = model_id or agent_settings.nova_lite

    # Create explicit boto3 session and client (proven working pattern)
    session = boto3.Session()
    bedrock_client = session.client('bedrock-runtime', region_name=agent_settings.aws_region)
    
    # Build additional context if user_id provided
    additional_context = ""
    if user_id:
        additional_context = f"\n<context>You are interacting with user: {user_id}</context>"

    return Agent(
        name="Sage",
        agent_id="sage",
        user_id=user_id,
        session_id=session_id,
        
        # AWS Bedrock with explicit client (this prevents runtime warnings!)
        model=AwsBedrock(
            id=model_id,
            client=bedrock_client  # Key: explicit client fixes async issues
        ),
        
        # Simple memory configuration (like working sample)
        memory=AgentMemory(),
        
        # System message with comprehensive instructions
        system_message=dedent(f"""\
            You are Sage, an advanced Knowledge Agent designed to deliver accurate, context-rich, and engaging responses.
            You have access to a comprehensive knowledge base and web search capabilities.

            Your core capabilities:
            - Search your knowledge base for relevant information
            - Search the web when needed for current information
            - Maintain conversation context and memory
            - Provide clear, well-structured responses with proper citations

            Response Guidelines:
            1. **Always search your knowledge base first** for relevant information
            2. **Use web search** if knowledge base results are insufficient
            3. **Start with a direct answer** to the user's question
            4. **Expand with context** including explanations, examples, and supporting evidence
            5. **Include proper citations** from both knowledge base and web sources
            6. **Maintain conversation flow** by referencing previous interactions when relevant
            7. **Ask follow-up questions** to enhance engagement

            Keep responses clear, concise, and well-structured. Avoid unnecessary hedging.
            {additional_context}
        """),
        
        # Essential tools
        tools=[DuckDuckGoTools()],
        
        # Storage and knowledge base (keeping your existing PostgreSQL setup)
        storage=PostgresAgentStorage(table_name="sage_sessions", db_url=db_url),
        knowledge=AgentKnowledge(
            vector_db=PgVector(table_name="sage_knowledge", db_url=db_url, search_type=SearchType.hybrid)
        ),
        
        # Core settings (optimized for reliability)
        description="Advanced knowledge agent with web search and knowledge base capabilities",
        markdown=True,
        add_datetime_to_instructions=True,
        add_history_to_messages=True,
        num_history_responses=3,
        read_chat_history=True,
        debug_mode=debug_mode,
        monitoring=True,
        
        # Note: We don't set stream=True here to avoid async issues
        # Streaming will be handled at the API route level when explicitly requested
    )
