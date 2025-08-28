#!/usr/bin/env python3
"""Main orchestration script for the agent prototype."""

import asyncio
import os
from typing import Optional
from dotenv import load_dotenv

from src.agent_prototype.agent.claude_agent import ClaudeAgent, AgentConfig


async def run_interactive_session(agent: ClaudeAgent):
    """Run an interactive chat session with the agent."""
    print("\n🤖 Claude Agent with MCP Tools")
    print("=" * 50)
    print("Type 'quit', 'exit', or press Ctrl+C to end the session")
    print("Type 'clear' to clear conversation history")
    print("Type 'tools' to see available tools")
    print("=" * 50)
    
    # Show available tools
    tools = await agent.get_available_tools()
    print(f"\n📦 Available tools ({len(tools)}):")
    for tool in tools:
        print(f"  • {tool['name']}: {tool['description']}")
    
    print("\n💬 Start chatting:")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'clear':
                agent.clear_conversation()
                print("🧹 Conversation history cleared!")
                continue
            elif user_input.lower() == 'tools':
                tools = await agent.get_available_tools()
                print(f"\n📦 Available tools ({len(tools)}):")
                for tool in tools:
                    print(f"  • {tool['name']}: {tool['description']}")
                continue
            elif not user_input:
                continue
            
            print("\nAgent: ", end="", flush=True)
            response = await agent.chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Session ended by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


async def run_demo_mode(agent: ClaudeAgent):
    """Run a demonstration of agent capabilities."""
    print("\n🎯 Agent Capability Demo")
    print("=" * 30)
    
    demo_queries = [
        "What tools do you have available?",
        "Search the web for 'artificial intelligence trends 2024'",
        "Analyze this Python code: 'def factorial(n): return 1 if n <= 1 else n * factorial(n-1)'",
        "Get system information",
        "Process this data: [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}] and sort it"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n📝 Demo Query {i}: {query}")
        print("-" * 50)
        
        response = await agent.chat(query)
        print(f"🤖 Response: {response}")
        
        await asyncio.sleep(1)  # Brief pause between queries


async def main():
    """Main entry point."""
    load_dotenv()
    
    # Configuration
    config = AgentConfig(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        temperature=0.7
    )
    
    if not config.api_key:
        print("❌ Error: ANTHROPIC_API_KEY not found in environment variables")
        print("Please set your Anthropic API key in a .env file or environment variable")
        return
    
    # Create agent
    agent = ClaudeAgent(config)
    
    print("🚀 Starting Agent Prototype")
    print(f"   Model: {config.model}")
    print(f"   Max tokens: {config.max_tokens}")
    print(f"   Temperature: {config.temperature}")
    
    # Check command line arguments
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        await run_demo_mode(agent)
    else:
        await run_interactive_session(agent)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
