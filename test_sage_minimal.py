#!/usr/bin/env python3
"""
Minimal test for Sage agent without storage dependencies
"""

import boto3
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.memory.agent import AgentMemory
from agno.tools.duckduckgo import DuckDuckGoTools

def test_minimal_sage():
    """Test minimal sage setup with AWS Bedrock"""
    print("🧪 Testing minimal Sage agent...")
    
    try:
        # Create explicit boto3 session and client (proven working pattern)
        session = boto3.Session()
        bedrock_client = session.client('bedrock-runtime', region_name='us-east-1')
        
        # Create minimal agent (no storage/knowledge dependencies)
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
        print(f"📋 Agent name: {agent.name}")
        print(f"📋 Model ID: {agent.model.id}")
        print(f"📋 Has tools: {len(agent.tools)}")
        print(f"📋 Has memory: {agent.memory is not None}")
        
        # Test simple query
        print("📝 Testing simple query...")
        response = agent.run("Hello! Just say 'Working' if you can see this.")
        print(f"✅ Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Minimal Sage Test")
    print("=" * 30)
    success = test_minimal_sage()
    if success:
        print("🎉 Minimal test passed!")
    else:
        print("❌ Test failed") 