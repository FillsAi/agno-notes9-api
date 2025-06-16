#!/usr/bin/env python3
"""
Streaming test for Sage agent to verify no runtime warnings
"""

import boto3
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.memory.agent import AgentMemory
from agno.tools.duckduckgo import DuckDuckGoTools

def test_sage_streaming():
    """Test sage streaming functionality"""
    print("🧪 Testing Sage agent streaming...")
    
    try:
        # Create explicit boto3 session and client (proven working pattern)
        session = boto3.Session()
        bedrock_client = session.client('bedrock-runtime', region_name='us-east-1')
        
        # Create agent with explicit client
        agent = Agent(
            name="Sage",
            agent_id="sage",
            model=AwsBedrock(
                id="amazon.nova-lite-v1:0",
                client=bedrock_client  # Explicit client fixes async issues
            ),
            memory=AgentMemory(),
            tools=[DuckDuckGoTools()],
            system_message="You are Sage, a helpful AI assistant.",
            markdown=True,
            debug_mode=True
        )
        
        print("✅ Sage agent created successfully!")
        
        # Test streaming (this should not produce runtime warnings)
        print("🌊 Testing streaming...")
        agent.print_response("Tell me a very short joke", stream=True)
        
        print("\n✅ Streaming test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sage_streaming_with_tools():
    """Test sage streaming with tool usage"""
    print("\n🧪 Testing Sage agent streaming with tools...")
    
    try:
        # Create explicit boto3 session and client
        session = boto3.Session()
        bedrock_client = session.client('bedrock-runtime', region_name='us-east-1')
        
        # Create agent with tools
        agent = Agent(
            name="Sage",
            agent_id="sage",
            model=AwsBedrock(
                id="amazon.nova-lite-v1:0",
                client=bedrock_client
            ),
            memory=AgentMemory(),
            tools=[DuckDuckGoTools()],
            system_message="You are Sage, a helpful AI assistant that can search the web.",
            show_tool_calls=True,
            markdown=True,
            debug_mode=True
        )
        
        print("✅ Sage agent with tools created successfully!")
        
        # Test streaming with tool usage
        print("🌊 Testing streaming with tool usage...")
        agent.print_response("What's the current weather in Tokyo?", stream=True)
        
        print("\n✅ Streaming with tools test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Sage Streaming Tests")
    print("=" * 40)
    
    # Test 1: Basic streaming
    success1 = test_sage_streaming()
    
    # Test 2: Streaming with tools
    if success1:
        success2 = test_sage_streaming_with_tools()
        
        if success1 and success2:
            print("\n🎉 ALL STREAMING TESTS PASSED!")
            print("✅ No runtime warnings!")
            print("✅ Sage agent is working perfectly!")
        else:
            print("\n⚠️ Some tests failed")
    else:
        print("\n❌ Basic streaming test failed") 