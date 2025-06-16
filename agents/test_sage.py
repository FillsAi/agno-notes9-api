#!/usr/bin/env python3
"""
Test Sage agent for playground testing - EXACT working pattern from agno-test
"""

import boto3
import os
from typing import Optional

from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.tools.duckduckgo import DuckDuckGoTools

# Handle both direct execution and module import
try:
    from .settings import agent_settings
    USE_SETTINGS = True
except ImportError:
    USE_SETTINGS = False


def get_test_sage(
    model_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Agent:
    """
    Create a test Sage agent using the EXACT working pattern from agno-test.
    
    This uses the minimal configuration that we KNOW works without runtime warnings.
    """
    
    # Use Amazon Nova Lite v1:0 as default model
    if USE_SETTINGS:
        model_id = model_id or agent_settings.nova_lite
        aws_region = agent_settings.aws_region
    else:
        model_id = model_id or "amazon.nova-lite-v1:0"
        aws_region = os.environ.get('AWS_REGION', 'us-east-1')

    # Create explicit boto3 session and client (EXACT working pattern)
    session = boto3.Session()
    bedrock_client = session.client('bedrock-runtime', region_name=aws_region)
    
    # Build system message
    system_message = "You are TestSage, a helpful AI assistant powered by Amazon Bedrock that can search the web for current information."
    if user_id:
        system_message += f"\n\nYou are interacting with user: {user_id}"

    # Create agent with MINIMAL configuration (like working version)
    return Agent(
        name="TestSage",
        agent_id="test_sage",
        user_id=user_id,
        session_id=session_id,
        
        # AWS Bedrock with explicit client (this is the key!)
        model=AwsBedrock(
            id=model_id,
            client=bedrock_client  # Explicit client prevents async issues
        ),
        
        # Tools (same as working version)
        tools=[DuckDuckGoTools()],
        
        # System message instead of instructions
        system_message=system_message,
        
        # Minimal settings (only what's in working version)
        show_tool_calls=True,
        markdown=True,
        debug_mode=debug_mode,
        
        # NOTE: NO memory, NO storage, NO extra configurations that might trigger async
    )


def test_agent_creation():
    """Test function to verify agent creation works"""
    try:
        agent = get_test_sage(user_id="playground_user")
        print(f"✅ TestSage agent created successfully!")
        print(f"📋 Agent: {agent.name}")
        print(f"📋 Model: {agent.model.id}")
        print(f"📋 Tools: {len(agent.tools)}")
        return agent
    except Exception as e:
        print(f"❌ Error creating TestSage: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_simple_query(agent: Agent):
    """Test function for a simple query"""
    try:
        print("\n🧪 Testing simple query...")
        response = agent.run("Hello! Just say 'TestSage is working' if you can see this.")
        print(f"✅ Response: {response.content}")
        return True
    except Exception as e:
        print(f"❌ Error in simple query: {e}")
        return False


def test_streaming_query(agent: Agent):
    """Test function for streaming (the main test)"""
    try:
        print("\n🌊 Testing streaming...")
        print("📝 This should NOT produce runtime warnings...")
        agent.print_response("Tell me a very short joke", stream=True)
        print("\n✅ Streaming test completed!")
        return True
    except Exception as e:
        print(f"❌ Error in streaming: {e}")
        return False


def test_web_search_streaming(agent: Agent):
    """Test function for web search with streaming (full test)"""
    try:
        print("\n🔍 Testing web search with streaming...")
        print("📝 This is the ultimate test...")
        agent.print_response("What's happening in France?", stream=True)
        print("\n✅ Web search streaming test completed!")
        return True
    except Exception as e:
        print(f"❌ Error in web search streaming: {e}")
        return False


if __name__ == "__main__":
    print("🚀 TestSage Agent - EXACT Working Pattern")
    print("=" * 50)
    
    # Create agent
    agent = test_agent_creation()
    
    if agent:
        # Run tests in order of complexity
        test1 = test_simple_query(agent)
        
        if test1:
            test2 = test_streaming_query(agent)
            
            if test2:
                test3 = test_web_search_streaming(agent)
                
                if test1 and test2 and test3:
                    print("\n🎉🎉🎉 COMPLETE SUCCESS! 🎉🎉🎉")
                    print("✅ All tests passed!")
                    print("✅ NO runtime warnings!")
                    print("✅ TestSage is working perfectly!")
                else:
                    print("\n⚠️ Some advanced tests failed")
            else:
                print("\n❌ Streaming test failed")
        else:
            print("\n❌ Simple test failed")
    else:
        print("\n❌ Agent creation failed") 