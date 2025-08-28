"""Claude agent implementation with MCP client integration."""

from typing import Dict, Any, List, Optional
import asyncio
import json
import os
import subprocess
from anthropic import Anthropic
from pydantic import BaseModel
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from contextlib import AsyncExitStack


class Message(BaseModel):
    """Represents a conversation message."""
    role: str
    content: str


class AgentConfig(BaseModel):
    """Configuration for the Claude agent."""
    api_key: Optional[str] = None
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4000
    temperature: float = 0.7
    mcp_server_command: List[str] = ["python", "-m", "src.agent_prototype.mcp_server.server"]


class ClaudeAgent:
    """Claude agent with MCP client integration."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.client = Anthropic(
            api_key=config.api_key or os.getenv("ANTHROPIC_API_KEY")
        )
        self.conversation_history: List[Message] = []
        self.mcp_session: Optional[ClientSession] = None
        self.exit_stack: Optional[AsyncExitStack] = None
    
    async def connect_to_mcp_server(self):
        """Connect to the MCP server."""
        if self.mcp_session is not None:
            return
        
        self.exit_stack = AsyncExitStack()
        
        # Start the MCP server process and create client session
        server_config = StdioServerParameters(
            command=self.config.mcp_server_command[0],
            args=self.config.mcp_server_command[1:] if len(self.config.mcp_server_command) > 1 else []
        )
        server_params = stdio_client(server_config)
        read_stream, write_stream = await self.exit_stack.enter_async_context(server_params)
        
        # Create and initialize the client session
        self.mcp_session = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        await self.mcp_session.initialize()
    
    async def disconnect_from_mcp_server(self):
        """Disconnect from the MCP server."""
        if self.exit_stack:
            await self.exit_stack.aclose()
            self.exit_stack = None
            self.mcp_session = None
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools from MCP server."""
        if not self.mcp_session:
            await self.connect_to_mcp_server()
        
        result = await self.mcp_session.list_tools()
        
        # Convert MCP Tool objects to dictionaries
        tools = []
        for tool in result.tools:
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            })
        
        return tools
    
    def format_tools_for_claude(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format MCP tools for Claude's tool calling format."""
        return tools  # MCP tools are already in the correct format for Claude
    
    async def execute_tool_call(self, tool_name: str, tool_arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call via the MCP server."""
        if not self.mcp_session:
            await self.connect_to_mcp_server()
        
        try:
            result = await self.mcp_session.call_tool(tool_name, tool_arguments)
            
            # Extract text content from the result
            text_content = ""
            for content in result.content:
                if hasattr(content, 'text'):
                    text_content += content.text
            
            return {
                "success": True,
                "result": text_content,
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": str(e)
            }
    
    async def chat(self, user_message: str) -> str:
        """Chat with Claude using available tools."""
        # Add user message to conversation
        self.conversation_history.append(Message(role="user", content=user_message))
        
        # Get available tools
        available_tools = await self.get_available_tools()
        formatted_tools = self.format_tools_for_claude(available_tools)
        
        # Format conversation history for Claude
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in self.conversation_history
        ]
        
        try:
            # Make initial request to Claude
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=messages,
                tools=formatted_tools if formatted_tools else None
            )
            
            # Handle tool calls if present
            if response.content and any(block.type == "tool_use" for block in response.content):
                # Add Claude's response to conversation
                assistant_message = ""
                tool_results = []
                
                for block in response.content:
                    if block.type == "text":
                        assistant_message += block.text
                    elif block.type == "tool_use":
                        # Execute the tool call
                        tool_result = await self.execute_tool_call(
                            block.name,
                            block.input
                        )
                        
                        tool_results.append({
                            "tool_use_id": block.id,
                            "content": json.dumps(tool_result, indent=2)
                        })
                
                # Add assistant message and tool results to conversation
                if assistant_message:
                    self.conversation_history.append(
                        Message(role="assistant", content=assistant_message)
                    )
                
                # Send tool results back to Claude
                if tool_results:
                    messages.append({
                        "role": "assistant", 
                        "content": response.content
                    })
                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })
                    
                    # Get final response from Claude
                    final_response = self.client.messages.create(
                        model=self.config.model,
                        max_tokens=self.config.max_tokens,
                        temperature=self.config.temperature,
                        messages=messages,
                        tools=formatted_tools
                    )
                    
                    final_text = ""
                    for block in final_response.content:
                        if block.type == "text":
                            final_text += block.text
                    
                    self.conversation_history.append(
                        Message(role="assistant", content=final_text)
                    )
                    
                    return final_text
            
            # Handle regular text response
            response_text = ""
            for block in response.content:
                if block.type == "text":
                    response_text += block.text
            
            self.conversation_history.append(
                Message(role="assistant", content=response_text)
            )
            
            return response_text
            
        except Exception as e:
            error_message = f"Error communicating with Claude: {str(e)}"
            self.conversation_history.append(
                Message(role="assistant", content=error_message)
            )
            return error_message
    
    def get_conversation_history(self) -> List[Message]:
        """Get the current conversation history."""
        return self.conversation_history.copy()
    
    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation_history = []
    
    async def demonstrate_capabilities(self) -> str:
        """Demonstrate agent capabilities with available tools."""
        tools = await self.get_available_tools()
        
        demo_message = f"""Hello! I'm a Claude agent with access to the following tools:

{chr(10).join([f"• {tool['name']}: {tool['description']}" for tool in tools])}

You can ask me to use any of these tools to help you with various tasks. 
For example:
- "Search the web for Python tutorials"  
- "Analyze this code for issues"
- "Get system information"
- "Process this data and filter it"

What would you like me to help you with?"""
        
        return demo_message
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect_to_mcp_server()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect_from_mcp_server()