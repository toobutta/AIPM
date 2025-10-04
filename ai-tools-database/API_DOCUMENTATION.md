# AI Tools Database API Documentation

## Overview

The AI Tools Database API provides a comprehensive system for managing AI SDK tool and function definitions across multiple AI providers (OpenAI, Claude, Gemini, Mistral, Cohere).

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. This may change in future versions.

## API Endpoints

### Health Check

#### GET /health

Check the health status of the API and database.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "database_status": "connected",
  "supported_providers": ["openai", "claude", "gemini", "mistral", "cohere"]
}
```

### Providers

#### GET /api/providers

Get all supported AI providers.

**Response:**
```json
[
  {
    "id": 1,
    "name": "openai",
    "display_name": "OpenAI",
    "api_version": "v1",
    "description": "OpenAI API with function calling capabilities",
    "documentation_url": "https://platform.openai.com/docs/api-reference/function-calling",
    "schema_format": "json_schema",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
]
```

#### GET /api/providers/{provider_name}

Get a specific provider by name.

**Path Parameters:**
- `provider_name` (string): Provider name (e.g., "openai", "claude")

#### GET /api/providers/{provider_name}/info

Get detailed information about a provider including validation rules and field mappings.

**Response:**
```json
{
  "name": "claude",
  "display_name": "Claude",
  "validation_rules": {
    "required_fields": ["name", "description", "input_schema"],
    "input_schema_type": "object"
  },
  "field_mappings": {
    "name": "name",
    "description": "description",
    "parameters": "input_schema"
  },
  "is_supported": true
}
```

### Categories

#### GET /api/categories

Get all tool categories.

**Response:**
```json
[
  {
    "id": 1,
    "name": "utilities",
    "description": "General utility functions",
    "parent_id": null,
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

#### POST /api/categories

Create a new category.

**Request Body:**
```json
{
  "name": "new_category",
  "description": "Category description",
  "parent_id": 1
}
```

### Tools

#### GET /api/tools

Search and filter tools.

**Query Parameters:**
- `query` (string, optional): Search query for tool name or description
- `category_id` (integer, optional): Filter by category ID
- `provider` (string, optional): Filter by provider
- `tags` (string, optional): Comma-separated tag list
- `limit` (integer, default=20): Number of results to return (1-100)
- `offset` (integer, default=0): Number of results to skip

**Example:**
```
GET /api/tools?query=weather&category_id=1&limit=10
```

**Response:**
```json
{
  "tools": [
    {
      "id": 1,
      "name": "get_weather",
      "description": "Get current weather information",
      "category_id": 1,
      "standardized_schema": {...},
      "tags": ["weather", "location"],
      "is_public": true,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

#### GET /api/tools/{tool_id}

Get a specific tool by ID.

#### POST /api/tools

Create a new tool.

**Request Body:**
```json
{
  "name": "new_tool",
  "description": "Tool description",
  "category_id": 1,
  "standardized_schema": {
    "name": "new_tool",
    "description": "Tool description",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  "tags": ["tag1", "tag2"],
  "is_public": true
}
```

#### PUT /api/tools/{tool_id}

Update an existing tool.

#### DELETE /api/tools/{tool_id}

Delete a tool.

### Schema Conversion

#### POST /api/convert

Convert a schema from one provider format to another.

**Request Body:**
```json
{
  "source_schema": {
    "name": "get_weather",
    "description": "Get current weather in a location",
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
```

**Response:**
```json
{
  "success": true,
  "target_schema": {
    "name": "get_weather",
    "description": "Get current weather in a location",
    "parameters": {
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
```

#### GET /api/tools/{tool_id}/convert/{provider}

Convert a tool's schema to a specific provider format.

### Validation

#### POST /api/validate

Validate a schema against provider-specific rules.

**Request Body:**
```json
{
  "schema": {
    "name": "get_weather",
    "description": "Get current weather information",
    "input_schema": {
      "type": "object",
      "properties": {
        "location": {"type": "string"}
      },
      "required": ["location"]
    }
  },
  "provider": "claude",
  "strict": false
}
```

**Response:**
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": [],
  "error_count": 0,
  "warning_count": 0
}
```

#### POST /api/validate/batch

Validate multiple schemas at once.

**Request Body:**
```json
{
  "schemas": [
    {...schema1...},
    {...schema2...}
  ],
  "providers": ["claude", "openai"],
  "strict": false
}
```

### Examples

#### GET /api/examples

Get conversion examples showing how schemas are transformed between providers.

#### GET /api/examples/{tool_name}

Get an example tool schema for a specific provider.

**Path Parameters:**
- `tool_name` (string): Example tool name
- `provider` (query): Provider name

#### POST /api/populate-examples

Populate the database with pre-defined example tools.

### Tool Schemas

#### GET /api/tools/{tool_id}/schemas

Get all provider-specific schemas for a tool.

#### POST /api/tools/{tool_id}/schemas

Create a provider-specific schema for a tool.

### Tool Examples

#### GET /api/tools/{tool_id}/examples

Get usage examples for a tool, optionally filtered by provider.

**Query Parameters:**
- `provider` (string, optional): Filter by provider

#### POST /api/tools/{tool_id}/examples

Create a new usage example for a tool.

## Error Responses

The API returns standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Data Models

### Standardized Schema Format

The database uses a standardized schema format based on Claude's input_schema:

```json
{
  "name": "tool_name",
  "description": "Tool description",
  "parameters": {
    "type": "object",
    "properties": {
      "param1": {
        "type": "string",
        "description": "Parameter description"
      },
      "param2": {
        "type": "integer",
        "description": "Another parameter",
        "minimum": 0
      }
    },
    "required": ["param1"]
  },
  "category": "category_name",
  "tags": ["tag1", "tag2"]
}
```

### Provider-Specific Formats

#### Claude (Anthropic)
```json
{
  "name": "tool_name",
  "description": "Tool description",
  "input_schema": {
    "type": "object",
    "properties": {...},
    "required": [...]
  }
}
```

#### OpenAI
```json
{
  "name": "tool_name",
  "description": "Tool description",
  "parameters": {
    "type": "object",
    "properties": {...},
    "required": [...]
  }
}
```

#### Mistral
```json
{
  "type": "function",
  "function": {
    "name": "tool_name",
    "description": "Tool description",
    "parameters": {
      "type": "object",
      "properties": {...},
      "required": [...]
    }
  }
}
```

## Usage Examples

### 1. Convert a Claude schema to OpenAI format

```bash
curl -X POST "http://localhost:8000/api/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "source_schema": {
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
  }'
```

### 2. Search for weather-related tools

```bash
curl "http://localhost:8000/api/tools?query=weather&limit=5"
```

### 3. Validate a schema

```bash
curl -X POST "http://localhost:8000/api/validate" \
  -H "Content-Type: application/json" \
  -d '{
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
    "strict": false
  }'
```

### 4. Create a new tool

```bash
curl -X POST "http://localhost:8000/api/tools" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_tool",
    "description": "My custom tool",
    "category_id": 1,
    "standardized_schema": {
      "name": "my_tool",
      "description": "My custom tool",
      "parameters": {
        "type": "object",
        "properties": {
          "input": {"type": "string"}
        },
        "required": ["input"]
      }
    },
    "tags": ["custom", "test"]
  }'
```

## SDK Integration

### Python Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Get all providers
response = requests.get(f"{BASE_URL}/api/providers")
providers = response.json()

# Convert schema
response = requests.post(f"{BASE_URL}/api/convert", json={
    "source_schema": {...},
    "source_provider": "claude",
    "target_provider": "openai"
})
result = response.json()

# Validate schema
response = requests.post(f"{BASE_URL}/api/validate", json={
    "schema": {...},
    "provider": "claude"
})
validation = response.json()
```

### JavaScript Example

```javascript
// Base URL
const BASE_URL = "http://localhost:8000";

// Get all tools
async function getTools(query = "", limit = 20) {
  const response = await fetch(
    `${BASE_URL}/api/tools?query=${query}&limit=${limit}`
  );
  return response.json();
}

// Convert schema
async function convertSchema(schema, fromProvider, toProvider) {
  const response = await fetch(`${BASE_URL}/api/convert`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      source_schema: schema,
      source_provider: fromProvider,
      target_provider: toProvider
    })
  });
  return response.json();
}
```

## Rate Limiting

Currently, there are no rate limits implemented. This may change in future versions.

## Support

For support and questions, please refer to the project documentation or create an issue in the repository.