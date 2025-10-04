# MCP Server Setup for AI Tools Database

## 🚀 Overview

This implementation provides an MCP (Model Context Protocol) server that allows AI assistants to interact with the AI Tools Database through Supabase.

## 📋 Prerequisites

1. **Supabase Database**: Set up and running with `schema.sql` executed
2. **Environment Variables**: Configure `.env` file with Supabase credentials
3. **Python Dependencies**: Install required packages including MCP

## 🛠️ Installation

1. **Install MCP SDK**:
```bash
pip install mcp==1.0.0
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
# Update .env with your Supabase credentials
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@YOUR_PROJECT_REF.supabase.co:5432/postgres
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY
```

## 🔧 MCP Configuration

### For Claude Desktop

Add this to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "ai-tools-database": {
      "command": "python",
      "args": ["/path/to/your/ai-tools-database/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/your/ai-tools-database",
        "DATABASE_URL": "postgresql://postgres:YOUR_PASSWORD@YOUR_PROJECT_REF.supabase.co:5432/postgres",
        "SUPABASE_URL": "https://YOUR_PROJECT_REF.supabase.co",
        "SUPABASE_ANON_KEY": "YOUR_SUPABASE_ANON_KEY"
      }
    }
  }
}
```

### For VS Code with MCP Extension

1. Install the MCP extension
2. Add the configuration to your VS Code settings

### Testing MCP Server Locally

```bash
# Run the MCP server directly
python mcp_server.py
```

## 🎯 Available Tools

### 1. `search_ai_tools`
Search for AI tools and function definitions.

**Parameters:**
- `query` (string): Search query for tool names or descriptions
- `category` (string): Filter by category name
- `provider` (string): Filter by provider (openai, claude, gemini, mistral, cohere)
- `tags` (array): Filter by tags
- `limit` (integer): Maximum number of results (default: 10)

**Example:**
```json
{
  "name": "search_ai_tools",
  "arguments": {
    "query": "weather",
    "provider": "openai",
    "limit": 5
  }
}
```

### 2. `get_ai_tool`
Get detailed information about a specific AI tool.

**Parameters:**
- `tool_id` (integer): Database ID of the tool
- `tool_name` (string): Name of the tool (alternative to tool_id)

**Example:**
```json
{
  "name": "get_ai_tool",
  "arguments": {
    "tool_name": "get_weather"
  }
}
```

### 3. `convert_tool_schema`
Convert an AI tool schema between different provider formats.

**Parameters:**
- `schema` (object): Tool schema to convert
- `source_provider` (string): Current provider format
- `target_provider` (string): Target provider format

**Example:**
```json
{
  "name": "convert_tool_schema",
  "arguments": {
    "schema": {
      "name": "get_weather",
      "description": "Get current weather",
      "input_schema": {
        "type": "object",
        "properties": {
          "location": {"type": "string"}
        },
        "required": ["location"]
      }
    },
    "source_provider": "claude",
    "target_provider": "openai"
  }
}
```

### 4. `validate_tool_schema`
Validate an AI tool schema against provider-specific rules.

**Parameters:**
- `schema` (object): Tool schema to validate
- `provider` (string): Provider to validate against
- `strict` (boolean): Enable strict validation mode (default: false)

**Example:**
```json
{
  "name": "validate_tool_schema",
  "arguments": {
    "schema": {
      "name": "test_tool",
      "description": "Test tool",
      "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
      }
    },
    "provider": "claude",
    "strict": true
  }
}
```

### 5. `list_providers`
List all supported AI providers with their capabilities.

**Example:**
```json
{
  "name": "list_providers",
  "arguments": {}
}
```

### 6. `list_categories`
List all tool categories for organizing and browsing tools.

**Example:**
```json
{
  "name": "list_categories",
  "arguments": {}
}
```

### 7. `get_tool_examples`
Get usage examples for a specific tool.

**Parameters:**
- `tool_id` (integer): Database ID of the tool
- `provider` (string): Filter examples by provider

**Example:**
```json
{
  "name": "get_tool_examples",
  "arguments": {
    "tool_id": 1,
    "provider": "openai"
  }
}
```

## 📚 Available Resources

### 1. `data://providers`
List of supported AI providers with their capabilities.

### 2. `data://categories`
Categories for organizing AI tools.

### 3. `data://examples`
Pre-built example AI tools with schemas.

## 🔍 Testing the MCP Server

### Test Script

```python
import asyncio
import json
from mcp_server import AIToolsMCPServer

async def test_mcp():
    server = AIToolsMCPServer()

    # Test provider listing
    result = await server._list_providers({})
    print("Providers:", result.content[0].text)

    # Test tool search
    result = await server._search_tools({"query": "weather", "limit": 3})
    print("Search Results:", result.content[0].text)

if __name__ == "__main__":
    asyncio.run(test_mcp())
```

### Manual Testing

1. Start the MCP server:
```bash
python mcp_server.py
```

2. Use your MCP client (Claude Desktop, VS Code, etc.) to make tool calls

## 🚨 Troubleshooting

### Common Issues

1. **Supabase Connection Failed**
   - Check your `DATABASE_URL` in `.env`
   - Verify your Supabase project is active
   - Ensure you've executed `schema.sql` in Supabase

2. **MCP Server Not Starting**
   - Check Python path configuration
   - Verify all dependencies are installed
   - Check for syntax errors in `mcp_server.py`

3. **Tool Calls Failing**
   - Check Supabase credentials in environment variables
   - Verify database tables exist
   - Check MCP client configuration

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎯 Use Cases

### For AI Assistants

1. **Discover Tools**: Search for relevant AI tools by functionality
2. **Format Conversion**: Convert schemas between AI providers
3. **Validation**: Ensure tool schemas meet provider requirements
4. **Examples**: Get usage examples for implementation

### For Developers

1. **Tool Management**: Browse and manage tool definitions
2. **Format Translation**: Convert between provider formats
3. **Quality Assurance**: Validate tool schemas
4. **Documentation**: Access tool examples and documentation

## 📝 Notes

- The MCP server uses Supabase for data storage
- All operations are read-only by default
- Schema conversion is done locally without external dependencies
- Validation includes provider-specific rules and best practices
- Resource endpoints provide static data for quick access

## 🔗 Integration

This MCP server can be integrated with:
- Claude Desktop
- VS Code with MCP extension
- Any MCP-compatible client
- Custom applications using the MCP SDK

For more information about MCP, see the [MCP documentation](https://modelcontextprotocol.io/).