"""Test configuration for pytest."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_readme_content():
    """Sample README content for testing."""
    return """# Test AI Tool

This is a test AI tool that provides various functionality.

## Features

- API endpoint for function calls
- Python SDK available
- OpenAI GPT-4 integration

## Usage

```python
def test_function(param1: str, param2: int) -> str:
    \"\"\"Test function example.\"\"\"
    return f"Hello {param1} with {param2}"
```

## Installation

```bash
pip install test-ai-tool
```
"""


@pytest.fixture
def sample_openapi_spec():
    """Sample OpenAPI specification for testing."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Test API",
            "version": "1.0.0",
            "description": "A test API for AI tools"
        },
        "servers": [
            {"url": "https://api.test.com/v1"}
        ],
        "paths": {
            "/generate": {
                "post": {
                    "operationId": "generate_text",
                    "summary": "Generate text using AI",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "prompt": {
                                            "type": "string",
                                            "description": "The input prompt"
                                        },
                                        "max_tokens": {
                                            "type": "integer",
                                            "description": "Maximum tokens to generate"
                                        }
                                    },
                                    "required": ["prompt"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Generated text",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "text": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }


@pytest.fixture
def sample_mcp_config():
    """Sample MCP configuration for testing."""
    return {
        "name": "test-mcp-tool",
        "version": "1.0.0",
        "description": "Test MCP tool configuration",
        "capabilities": {
            "tools": True,
            "resources": True
        },
        "tools": {
            "search_web": {
                "description": "Search the web for information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of results",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    }


@pytest.fixture
def temp_repos_file(tmp_path):
    """Create a temporary repos.txt file."""
    repos_file = tmp_path / "repos.txt"
    repos_file.write_text("""https://github.com/test/repo1
https://github.com/example/repo2
# Comment line
https://github.com/demo/repo3
""")
    return str(repos_file)