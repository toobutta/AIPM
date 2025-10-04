"""
Format conversion utilities for AI SDK tool schemas
"""

import json
from typing import Dict, Any, Optional
from provider_schemas import ProviderType, get_provider_schema, STANDARD_SCHEMA_TEMPLATE

class SchemaConverter:
    """Convert tool schemas between different AI provider formats"""

    def __init__(self):
        self.provider_schemas = {
            provider.value: get_provider_schema(provider)
            for provider in ProviderType
        }

    def convert_schema(self,
                      source_schema: Dict[str, Any],
                      source_provider: str,
                      target_provider: str) -> Dict[str, Any]:
        """
        Convert schema from one provider format to another

        Args:
            source_schema: Original schema in source provider format
            source_provider: Name of source provider ('openai', 'claude', etc.)
            target_provider: Name of target provider ('openai', 'claude', etc.)

        Returns:
            Converted schema in target provider format
        """
        # Convert to standardized format first
        standardized = self._to_standardized(source_schema, source_provider)

        # Convert from standardized to target format
        return self._from_standardized(standardized, target_provider)

    def _to_standardized(self, schema: Dict[str, Any], provider: str) -> Dict[str, Any]:
        """Convert provider-specific schema to standardized format"""
        if provider not in self.provider_schemas:
            raise ValueError(f"Unsupported source provider: {provider}")

        provider_schema = self.provider_schemas[provider]

        # Handle provider-specific wrapper formats
        if provider == "mistral":
            schema = self._unwrap_mistral_schema(schema)

        return provider_schema.convert_to_standard(schema)

    def _from_standardized(self, standardized: Dict[str, Any], provider: str) -> Dict[str, Any]:
        """Convert standardized schema to provider-specific format"""
        if provider not in self.provider_schemas:
            raise ValueError(f"Unsupported target provider: {provider}")

        provider_schema = self.provider_schemas[provider]
        converted = provider_schema.convert_from_standard(standardized)

        # Handle provider-specific wrapper formats
        if provider == "mistral":
            converted = self._wrap_mistral_schema(converted)

        return converted

    def _unwrap_mistral_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract function definition from Mistral wrapper format"""
        if schema.get("type") == "function" and "function" in schema:
            return schema["function"]
        return schema

    def _wrap_mistral_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Wrap function definition in Mistral format"""
        return {
            "type": "function",
            "function": schema
        }

    def validate_schema(self, schema: Dict[str, Any], provider: str) -> bool:
        """Validate schema against provider-specific rules"""
        if provider not in self.provider_schemas:
            raise ValueError(f"Unsupported provider: {provider}")

        provider_schema = self.provider_schemas[provider]
        validation_rules = provider_schema.validation_rules

        # Check required fields
        required_fields = validation_rules.get("required_fields", [])
        for field in required_fields:
            if field not in schema:
                return False

        # Validate parameters structure
        if "parameters" in schema or "input_schema" in schema:
            params = schema.get("parameters") or schema.get("input_schema", {})
            if not isinstance(params, dict):
                return False

            if params.get("type") != "object":
                return False

        return True

    def get_supported_providers(self) -> list:
        """Get list of supported providers"""
        return list(self.provider_schemas.keys())

    def get_provider_info(self, provider: str) -> Dict[str, Any]:
        """Get information about a specific provider"""
        if provider not in self.provider_schemas:
            raise ValueError(f"Unsupported provider: {provider}")

        provider_schema = self.provider_schemas[provider]
        return {
            "name": provider,
            "display_name": provider.replace("_", " ").title(),
            "validation_rules": provider_schema.validation_rules,
            "field_mappings": provider_schema.field_mappings
        }

class StandardizedSchema:
    """Helper class for working with standardized schemas"""

    @staticmethod
    def create(name: str,
               description: str,
               parameters: Dict[str, Any],
               category: str = "",
               tags: Optional[list] = None) -> Dict[str, Any]:
        """Create a standardized schema"""
        schema = STANDARD_SCHEMA_TEMPLATE.copy()
        schema.update({
            "name": name,
            "description": description,
            "parameters": parameters,
            "category": category,
            "tags": tags or []
        })
        return schema

    @staticmethod
    def validate_standardized(schema: Dict[str, Any]) -> bool:
        """Validate a standardized schema"""
        required_fields = ["name", "description", "parameters"]

        for field in required_fields:
            if field not in schema:
                return False

        # Validate parameters structure
        params = schema["parameters"]
        if not isinstance(params, dict) or params.get("type") != "object":
            return False

        # Validate properties
        properties = params.get("properties", {})
        if not isinstance(properties, dict):
            return False

        # Validate required array
        required = params.get("required", [])
        if not isinstance(required, list):
            return False

        # Validate all required fields are in properties
        for req_field in required:
            if req_field not in properties:
                return False

        return True

    @staticmethod
    def extract_parameters(schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and clean parameters from a schema"""
        if "parameters" in schema:
            return schema["parameters"]
        elif "input_schema" in schema:
            return schema["input_schema"]
        return {}

    @staticmethod
    def add_example(schema: Dict[str, Any], example: Dict[str, Any]) -> Dict[str, Any]:
        """Add an example to a schema"""
        if "examples" not in schema:
            schema["examples"] = []
        schema["examples"].append(example)
        return schema

# Global converter instance
converter = SchemaConverter()

# Conversion examples
def get_conversion_examples():
    """Get examples of schema conversions"""
    examples = {
        "claude_to_openai": {
            "source": {
                "name": "get_weather",
                "description": "Get current weather in a location",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City and state, e.g. San Francisco, CA"
                        }
                    },
                    "required": ["location"]
                }
            },
            "target": {
                "name": "get_weather",
                "description": "Get current weather in a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City and state, e.g. San Francisco, CA"
                        }
                    },
                    "required": ["location"]
                }
            }
        },
        "openai_to_mistral": {
            "source": {
                "name": "web_search",
                "description": "Search the web",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    },
                    "required": ["query"]
                }
            },
            "target": {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                }
            }
        }
    }
    return examples