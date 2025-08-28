"""MCP Server implementation using the official mcp package."""

from typing import Any
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from ..tools.placeholder_tools import (
    web_search,
    file_operations, 
    code_analysis,
    data_processing,
    system_info
)

# Create the MCP server
server = Server("agent-prototype-server")

# Define tools
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="web_search",
            description="Search the web for information",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="file_operations",
            description="Perform file operations (read, write, delete, list)",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "Type of operation to perform",
                        "enum": ["read", "write", "delete", "list"]
                    },
                    "path": {
                        "type": "string",
                        "description": "File or directory path"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write (only for write operation)"
                    }
                },
                "required": ["operation", "path"]
            }
        ),
        Tool(
            name="code_analysis",
            description="Analyze code for issues and suggestions",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to analyze"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language",
                        "default": "python"
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="data_processing",
            description="Process data with various operations",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "description": "Data to process"
                    },
                    "operation": {
                        "type": "string",
                        "description": "Operation to perform on the data"
                    }
                },
                "required": ["data", "operation"]
            }
        ),
        Tool(
            name="system_info",
            description="Get system information",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "web_search":
            result = await web_search(**arguments)
        elif name == "file_operations":
            result = await file_operations(**arguments)
        elif name == "code_analysis":
            result = await code_analysis(**arguments)
        elif name == "data_processing":
            result = await data_processing(**arguments)
        elif name == "system_info":
            result = await system_info(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return [TextContent(type="text", text=str(result))]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())