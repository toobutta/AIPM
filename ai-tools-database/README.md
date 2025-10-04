# AI SDK Tool & Function Definition Database

A comprehensive database system for storing and managing AI SDK tool and function definitions across multiple AI providers (OpenAI, Claude, Gemini, Mistral, Cohere, etc.).

## Features

- **Multi-Provider Support**: Store tool definitions for OpenAI, Claude, Gemini, Mistral, and other major AI providers
- **Format Conversion**: Automatic translation between different provider schema formats
- **Validation**: JSON Schema validation for each provider's requirements
- **Search & Discovery**: Find tools by function, provider, or capabilities
- **Example Library**: Pre-built common tools with usage examples
- **RESTful API**: Complete API for tool management and conversion

## Quick Start

1. **Setup Database**:
   ```sql
   psql -d your_database -f schema.sql
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the API**:
   ```bash
   uvicorn main:app --reload
   ```

## Database Schema

The database consists of several key tables:

- **providers**: AI provider information (OpenAI, Claude, etc.)
- **tools**: Standardized tool definitions
- **provider_schemas**: Provider-specific schema variations
- **tool_examples**: Usage examples for each provider
- **field_mappings**: Format conversion mappings
- **validation_rules**: Provider-specific validation rules

## API Endpoints

- `GET /api/providers` - List all supported providers
- `GET /api/tools` - Search and filter tools
- `POST /api/tools` - Create new tool
- `GET /api/tools/{id}/convert/{provider}` - Convert tool to provider format
- `POST /api/tools/validate` - Validate tool schema
- `GET /api/tools/{id}/examples/{provider}` - Get tool examples

## Provider Schema Formats

### Claude (Anthropic)
```json
{
  "name": "get_weather",
  "description": "Get current weather in a location",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": {"type": "string"},
      "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
    },
    "required": ["location"]
  }
}
```

### OpenAI
```json
{
  "name": "get_weather",
  "description": "Get current weather in a location",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {"type": "string"},
      "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
    },
    "required": ["location"]
  }
}
```

## Development

The project uses:
- **FastAPI** for the REST API
- **SQLAlchemy** for ORM
- **PostgreSQL** with JSONB support
- **JSON Schema** for validation
- **Pydantic** for data models

## License

MIT License