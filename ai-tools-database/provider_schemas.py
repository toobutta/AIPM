"""
Provider-specific schema definitions for AI SDK tool formats
"""

from typing import Dict, Any, List
from enum import Enum

class ProviderType(Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    MISTRAL = "mistral"
    COHERE = "cohere"

class ProviderSchema:
    """Base class for provider-specific schemas"""

    def __init__(self, provider: ProviderType):
        self.provider = provider
        self.field_mappings = self._get_field_mappings()
        self.validation_rules = self._get_validation_rules()

    def _get_field_mappings(self) -> Dict[str, str]:
        """Get field mappings from standardized format to provider format"""
        return {}

    def _get_validation_rules(self) -> Dict[str, Any]:
        """Get provider-specific validation rules"""
        return {}

    def convert_from_standard(self, standard_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Convert from standardized schema to provider format"""
        result = {}
        for standard_field, provider_field in self.field_mappings.items():
            if standard_field in standard_schema:
                result[provider_field] = standard_schema[standard_field]
        return result

    def convert_to_standard(self, provider_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Convert from provider format to standardized format"""
        result = {}
        for provider_field, standard_field in {v: k for k, v in self.field_mappings.items()}.items():
            if provider_field in provider_schema:
                result[standard_field] = provider_schema[provider_field]
        return result

class ClaudeSchema(ProviderSchema):
    """Claude (Anthropic) schema format"""

    def __init__(self):
        super().__init__(ProviderType.CLAUDE)

    def _get_field_mappings(self) -> Dict[str, str]:
        return {
            "name": "name",
            "description": "description",
            "parameters": "input_schema"
        }

    def _get_validation_rules(self) -> Dict[str, Any]:
        return {
            "required_fields": ["name", "description", "input_schema"],
            "input_schema_type": "object",
            "supports_nested_objects": True,
            "supports_arrays": True,
            "supports_enum": True
        }

class OpenAISchema(ProviderSchema):
    """OpenAI schema format"""

    def __init__(self):
        super().__init__(ProviderType.OPENAI)

    def _get_field_mappings(self) -> Dict[str, str]:
        return {
            "name": "name",
            "description": "description",
            "parameters": "parameters"
        }

    def _get_validation_rules(self) -> Dict[str, Any]:
        return {
            "required_fields": ["name", "description", "parameters"],
            "parameters_type": "object",
            "supports_nested_objects": True,
            "supports_arrays": True,
            "supports_enum": True,
            "function_wrapper": True
        }

class GeminiSchema(ProviderSchema):
    """Google Gemini schema format"""

    def __init__(self):
        super().__init__(ProviderType.GEMINI)

    def _get_field_mappings(self) -> Dict[str, str]:
        return {
            "name": "name",
            "description": "description",
            "parameters": "parameters"
        }

    def _get_validation_rules(self) -> Dict[str, Any]:
        return {
            "required_fields": ["name", "description", "parameters"],
            "parameters_type": "object",
            "uses_openapi_schema": True,
            "supports_nested_objects": True,
            "supports_arrays": True,
            "supports_enum": True
        }

class MistralSchema(ProviderSchema):
    """Mistral AI schema format"""

    def __init__(self):
        super().__init__(ProviderType.MISTRAL)

    def _get_field_mappings(self) -> Dict[str, str]:
        return {
            "name": "name",
            "description": "description",
            "parameters": "parameters"
        }

    def _get_validation_rules(self) -> Dict[str, Any]:
        return {
            "required_fields": ["type", "function"],
            "function_type": "object",
            "supports_nested_objects": True,
            "supports_arrays": True,
            "supports_enum": True,
            "wrapper_format": {
                "type": "function",
                "function": {
                    "name": "{{name}}",
                    "description": "{{description}}",
                    "parameters": "{{parameters}}"
                }
            }
        }

class CohereSchema(ProviderSchema):
    """Cohere schema format"""

    def __init__(self):
        super().__init__(ProviderType.COHERE)

    def _get_field_mappings(self) -> Dict[str, str]:
        return {
            "name": "name",
            "description": "description",
            "parameters": "parameter_definitions"
        }

    def _get_validation_rules(self) -> Dict[str, Any]:
        return {
            "required_fields": ["name", "description", "parameter_definitions"],
            "parameter_format": "definitions_object",
            "supports_nested_objects": True,
            "supports_arrays": True,
            "supports_enum": True,
            "type_descriptions": True
        }

# Provider registry
PROVIDER_SCHEMAS: Dict[ProviderType, type] = {
    ProviderType.CLAUDE: ClaudeSchema,
    ProviderType.OPENAI: OpenAISchema,
    ProviderType.GEMINI: GeminiSchema,
    ProviderType.MISTRAL: MistralSchema,
    ProviderType.COHERE: CohereSchema,
}

def get_provider_schema(provider: ProviderType) -> ProviderSchema:
    """Get provider schema instance"""
    if provider not in PROVIDER_SCHEMAS:
        raise ValueError(f"Unsupported provider: {provider}")
    return PROVIDER_SCHEMAS[provider]()

def list_supported_providers() -> List[str]:
    """List all supported providers"""
    return [provider.value for provider in ProviderType]

# Standardized schema format
STANDARD_SCHEMA_TEMPLATE = {
    "name": "",
    "description": "",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    },
    "category": "",
    "tags": [],
    "examples": []
}

# Example schemas for testing
EXAMPLE_TOOLS = {
    "weather": {
        "name": "get_weather",
        "description": "Get current weather information for a specific location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit"
                }
            },
            "required": ["location"]
        },
        "category": "utilities",
        "tags": ["weather", "location", "temperature"]
    },
    "search": {
        "name": "web_search",
        "description": "Search the web for information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return",
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["query"]
        },
        "category": "search",
        "tags": ["web", "search", "information"]
    },
    "database": {
        "name": "query_database",
        "description": "Execute a SQL query on a database",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL query to execute"
                },
                "database": {
                    "type": "string",
                    "description": "Database name"
                }
            },
            "required": ["query"]
        },
        "category": "data_access",
        "tags": ["database", "sql", "query"]
    }
}