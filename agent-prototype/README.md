# Agent Prototype

A prototype implementation of an AI agent using the Claude SDK with MCP (Model Context Protocol) server integration for tool access.

## Architecture Overview

This prototype demonstrates a modern, clean architecture with:

- **Claude Agent**: Main agent implementation using Anthropic's Claude SDK
- **FastMCP Server**: Modern MCP server using FastMCP with integrated tools
- **Tool Integration**: Tools defined directly in the server using decorators and docstrings
- **Interactive Interface**: Command-line interface for chatting with the agent

## Project Structure

```
agent-prototype/
├── src/agent_prototype/
│   ├── agent/
│   │   └── claude_agent.py    # Main agent implementation
│   └── mcp_server/
│       └── server.py          # FastMCP server with integrated tools
├── main.py                    # Entry point and orchestration
├── test_mcp.py               # MCP functionality tests
├── pyproject.toml            # uv project configuration
└── .env.example              # Environment configuration template
```

## Setup

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

3. **Run the agent**:
   ```bash
   # Interactive mode
   uv run main.py
   
   # Demo mode
   uv run main.py --demo
   ```

## Usage

### Interactive Mode
```bash
uv run main.py
```

The agent will start an interactive session where you can:
- Chat with Claude using available tools
- Type `tools` to see available tools with detailed descriptions
- Type `clear` to clear conversation history
- Type `quit` or `exit` to end the session

### Demo Mode
```bash
uv run main.py --demo
```

Runs a simple demonstration showing the agent's capabilities and available tools.

### Testing
```bash
uv run test_mcp.py
```

Tests MCP server-client communication and individual tool functionality.

## Available Tools

The prototype includes these integrated tools:

- **web_search**: Search the web for information with configurable result limits
- **file_operations**: Perform file operations (read, write, delete, list) on specified paths
- **code_analysis**: Analyze source code for issues and suggestions with language support
- **data_processing**: Process arrays of data objects with various operations
- **system_info**: Get comprehensive system information including platform and resource usage

Each tool provides detailed parameter descriptions and return value documentation through docstrings.

## Key Components

### ClaudeAgent (`src/agent_prototype/agent/claude_agent.py`)
- Manages conversation with Claude using the Anthropic SDK
- Handles tool calling and result processing with proper API formatting
- Maintains conversation history and manages MCP client sessions
- Provides async context manager support for resource cleanup

### FastMCP Server (`src/agent_prototype/mcp_server/server.py`)
- Built using the modern FastMCP framework for clean, maintainable code
- Tools defined directly with `@mcp.tool()` decorators
- Automatic schema generation from function signatures and docstrings
- Rich documentation support with detailed parameter descriptions
- Automatic input validation and error handling

## Extending the System

Adding new tools is now extremely simple with FastMCP:

```python
@mcp.tool()
async def my_new_tool(param1: str, param2: int = 10) -> Dict[str, Any]:
    """Brief description of what this tool does.
    
    Args:
        param1: Description of the first parameter
        param2: Description of the second parameter with default value
        
    Returns:
        Dictionary containing the tool's results
    """
    # Your tool implementation here
    return {"result": "success", "processed": param1}
```

**Benefits of this approach:**
- **Single source of truth**: Function signature defines the schema
- **Rich documentation**: Docstrings become tool descriptions automatically
- **Type safety**: FastMCP validates inputs against function signatures
- **No boilerplate**: No manual schema definitions or registrations needed
- **Maintainable**: Changes to function automatically update the tool interface

The agent will automatically discover and use any new tools added with the `@mcp.tool()` decorator.

## Configuration

Environment variables (in `.env`):
- `ANTHROPIC_API_KEY`: Your Anthropic API key (required)
- `CLAUDE_MODEL`: Claude model to use (default: claude-3-5-sonnet-20241022)
- `MAX_TOKENS`: Maximum response tokens (default: 4000)
- `TEMPERATURE`: Response temperature (default: 0.7)

## Development

This prototype uses modern Python tooling:
- **uv** for fast package management and virtual environments
- **FastMCP** for modern MCP server development
- **Pydantic** for data validation and type safety
- **Anthropic SDK** for Claude integration
- **Type hints** throughout for better developer experience

## Key Features

- **Clean Architecture**: No code duplication between tool definitions and schemas
- **Rich Documentation**: Tools automatically documented from docstrings
- **Type Safety**: Full type checking and validation
- **Modern Tooling**: Built with the latest Python ecosystem tools
- **Easy Testing**: Comprehensive test suite for MCP functionality
- **Professional Output**: FastMCP provides beautiful server startup information

The modular design with FastMCP makes this prototype easy to understand, extend, and maintain.