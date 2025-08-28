"""Test script to demonstrate MCP server-client communication."""

import asyncio
import os
from dotenv import load_dotenv

from src.agent_prototype.agent.claude_agent import ClaudeAgent, AgentConfig

# Load environment variables
load_dotenv()

async def main():
    """Test MCP server-client communication."""
    # Create agent configuration
    config = AgentConfig(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        temperature=0.7
    )
    
    print("=== MCP Server-Client Communication Test ===\n")
    
    # Use the agent as an async context manager
    async with ClaudeAgent(config) as agent:
        # Show available capabilities
        print("Testing MCP connection...")
        tools = await agent.get_available_tools()
        
        print(f"Successfully connected to MCP server!")
        print(f"Available tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        print("\n" + "="*50 + "\n")
        
        # Test each tool individually
        print("Testing individual tools...\n")
        
        # Test system info (no parameters needed)
        print("1. Testing system_info tool:")
        try:
            result = await agent.execute_tool_call("system_info", {})
            print(f"   Success: {result['success']}")
            print(f"   Result: {result['result']}")
        except Exception as e:
            print(f"   Error: {e}")
        
        print()
        
        # Test web search
        print("2. Testing web_search tool:")
        try:
            result = await agent.execute_tool_call("web_search", {"query": "MCP framework", "max_results": 3})
            print(f"   Success: {result['success']}")
            print(f"   Result: {result['result'][:200]}..." if len(str(result['result'])) > 200 else f"   Result: {result['result']}")
        except Exception as e:
            print(f"   Error: {e}")
        
        print()
        
        # Test file operations
        print("3. Testing file_operations tool:")
        try:
            result = await agent.execute_tool_call("file_operations", {"operation": "list", "path": "."})
            print(f"   Success: {result['success']}")
            print(f"   Result: {result['result'][:200]}..." if len(str(result['result'])) > 200 else f"   Result: {result['result']}")
        except Exception as e:
            print(f"   Error: {e}")
        
        print()
        
        # Test code analysis
        print("4. Testing code_analysis tool:")
        test_code = '''
def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n-1)
'''
        try:
            result = await agent.execute_tool_call("code_analysis", {"code": test_code, "language": "python"})
            print(f"   Success: {result['success']}")
            print(f"   Result: {result['result'][:200]}..." if len(str(result['result'])) > 200 else f"   Result: {result['result']}")
        except Exception as e:
            print(f"   Error: {e}")
        
        print()
        
        # Test data processing
        print("5. Testing data_processing tool:")
        try:
            test_data = [1, 2, 3, 4, 5]
            result = await agent.execute_tool_call("data_processing", {"data": test_data, "operation": "sum"})
            print(f"   Success: {result['success']}")
            print(f"   Result: {result['result']}")
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\n" + "="*50)
        print("MCP communication test completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())