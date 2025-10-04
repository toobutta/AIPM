"""
Validation system for AI SDK tool schemas
"""

import json
import jsonschema
from typing import Dict, Any, List, Optional, Tuple
from provider_schemas import ProviderType, get_provider_schema

class ValidationError:
    """Represents a validation error"""

    def __init__(self, field: str, message: str, error_type: str = "error"):
        self.field = field
        self.message = message
        self.error_type = error_type  # error, warning, info

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "message": self.message,
            "type": self.error_type
        }

class ValidationResult:
    """Container for validation results"""

    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.is_valid: bool = True

    def add_error(self, field: str, message: str):
        """Add a validation error"""
        self.errors.append(ValidationError(field, message, "error"))
        self.is_valid = False

    def add_warning(self, field: str, message: str):
        """Add a validation warning"""
        self.warnings.append(ValidationError(field, message, "warning"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": [error.to_dict() for error in self.errors],
            "warnings": [warning.to_dict() for warning in self.warnings],
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }

class SchemaValidator:
    """Main validator for AI SDK tool schemas"""

    def __init__(self):
        self.json_schema_validator = jsonschema.Draft7Validator

    def validate(self,
                 schema: Dict[str, Any],
                 provider: str,
                 strict: bool = False) -> ValidationResult:
        """
        Validate a schema against provider-specific rules

        Args:
            schema: Schema to validate
            provider: Provider name ('openai', 'claude', etc.)
            strict: Whether to treat warnings as errors

        Returns:
            ValidationResult with validation details
        """
        result = ValidationResult()

        try:
            provider_type = ProviderType(provider)
            provider_schema = get_provider_schema(provider_type)
            validation_rules = provider_schema.validation_rules

            # Validate against provider-specific rules
            self._validate_required_fields(schema, validation_rules, result)
            self._validate_parameters_structure(schema, validation_rules, result)
            self._validate_json_schema(schema, result)
            self._validate_field_names(schema, result)
            self._validate_descriptions(schema, result)
            self._validate_types(schema, result)

            # Provider-specific validations
            self._validate_provider_specific(schema, provider, validation_rules, result)

            # Apply strict mode
            if strict and result.warnings:
                for warning in result.warnings:
                    result.add_error(warning.field, warning.message)
                result.warnings.clear()

        except ValueError as e:
            result.add_error("provider", f"Unsupported provider: {e}")
        except Exception as e:
            result.add_error("validation", f"Validation error: {str(e)}")

        return result

    def _validate_required_fields(self,
                                 schema: Dict[str, Any],
                                 rules: Dict[str, Any],
                                 result: ValidationResult):
        """Validate required fields are present"""
        required_fields = rules.get("required_fields", [])

        for field in required_fields:
            if field not in schema:
                result.add_error(field, f"Required field '{field}' is missing")

    def _validate_parameters_structure(self,
                                     schema: Dict[str, Any],
                                     rules: Dict[str, Any],
                                     result: ValidationResult):
        """Validate parameters/input_schema structure"""
        # Find the parameters field (may be named differently)
        params_field = None
        for field_name in ["parameters", "input_schema", "parameter_definitions"]:
            if field_name in schema:
                params_field = field_name
                break

        if not params_field:
            result.add_error("parameters", "No parameters field found")
            return

        params = schema[params_field]

        if not isinstance(params, dict):
            result.add_error(params_field, "Parameters must be a JSON object")
            return

        expected_type = rules.get("parameters_type", rules.get("input_schema_type", "object"))
        if params.get("type") != expected_type:
            result.add_error(params_field, f"Parameters type must be '{expected_type}'")

        # Validate properties
        properties = params.get("properties", {})
        if not isinstance(properties, dict):
            result.add_error(params_field, "Properties must be a JSON object")
            return

        # Validate required fields in parameters
        required_fields = params.get("required", [])
        if not isinstance(required_fields, list):
            result.add_error(params_field, "Required fields must be an array")
            return

        # Check that all required fields exist in properties
        for req_field in required_fields:
            if req_field not in properties:
                result.add_error(params_field, f"Required field '{req_field}' not defined in properties")

    def _validate_json_schema(self,
                            schema: Dict[str, Any],
                            result: ValidationResult):
        """Validate against JSON Schema specification"""
        # Find parameters field
        params = None
        for field_name in ["parameters", "input_schema", "parameter_definitions"]:
            if field_name in schema:
                params = schema[field_name]
                break

        if not params or "properties" not in params:
            return

        properties = params["properties"]

        # Validate each property
        for prop_name, prop_def in properties.items():
            if not isinstance(prop_def, dict):
                result.add_error(f"properties.{prop_name}", "Property definition must be a JSON object")
                continue

            # Check type field
            if "type" not in prop_def:
                result.add_warning(f"properties.{prop_name}", "Property should have a 'type' field")
                continue

            # Validate enum values
            if "enum" in prop_def:
                enum_values = prop_def["enum"]
                if not isinstance(enum_values, list) or len(enum_values) == 0:
                    result.add_error(f"properties.{prop_name}.enum", "Enum must be a non-empty array")

            # Validate nested objects
            if prop_def.get("type") == "object" and "properties" in prop_def:
                if not isinstance(prop_def["properties"], dict):
                    result.add_error(f"properties.{prop_name}.properties", "Nested properties must be a JSON object")

    def _validate_field_names(self,
                            schema: Dict[str, Any],
                            result: ValidationResult):
        """Validate field naming conventions"""
        # Check tool name
        if "name" in schema:
            name = schema["name"]
            if not isinstance(name, str):
                result.add_error("name", "Tool name must be a string")
            elif not name.replace("_", "").replace("-", "").isalnum():
                result.add_warning("name", "Tool name should contain only alphanumeric characters, hyphens, and underscores")

        # Check description
        if "description" in schema:
            desc = schema["description"]
            if not isinstance(desc, str):
                result.add_error("description", "Description must be a string")
            elif len(desc) < 10:
                result.add_warning("description", "Description should be at least 10 characters long")

    def _validate_descriptions(self,
                             schema: Dict[str, Any],
                             result: ValidationResult):
        """Validate description fields"""
        # Find parameters field
        params = None
        for field_name in ["parameters", "input_schema", "parameter_definitions"]:
            if field_name in schema:
                params = schema[field_name]
                break

        if not params or "properties" not in params:
            return

        properties = params["properties"]

        # Check property descriptions
        for prop_name, prop_def in properties.items():
            if isinstance(prop_def, dict) and "description" not in prop_def:
                result.add_warning(f"properties.{prop_name}", "Property should have a description")

    def _validate_types(self,
                       schema: Dict[str, Any],
                       result: ValidationResult):
        """Validate type definitions"""
        # Find parameters field
        params = None
        for field_name in ["parameters", "input_schema", "parameter_definitions"]:
            if field_name in schema:
                params = schema[field_name]
                break

        if not params or "properties" not in params:
            return

        properties = params["properties"]
        valid_types = ["string", "number", "integer", "boolean", "object", "array"]

        for prop_name, prop_def in properties.items():
            if isinstance(prop_def, dict) and "type" in prop_def:
                prop_type = prop_def["type"]
                if prop_type not in valid_types:
                    result.add_error(f"properties.{prop_name}.type", f"Invalid type '{prop_type}'. Must be one of: {valid_types}")

    def _validate_provider_specific(self,
                                  schema: Dict[str, Any],
                                  provider: str,
                                  rules: Dict[str, Any],
                                  result: ValidationResult):
        """Provider-specific validation rules"""
        if provider == "mistral":
            self._validate_mistral_format(schema, result)
        elif provider == "cohere":
            self._validate_cohere_format(schema, result)
        elif provider == "gemini":
            self._validate_gemini_format(schema, rules, result)

    def _validate_mistral_format(self,
                               schema: Dict[str, Any],
                               result: ValidationResult):
        """Validate Mistral-specific format"""
        if schema.get("type") != "function":
            result.add_error("type", "Mistral schemas must have type 'function'")

        if "function" not in schema:
            result.add_error("function", "Mistral schemas must have a 'function' field")

        if isinstance(schema.get("function"), dict):
            func_schema = schema["function"]
            required_func_fields = ["name", "description", "parameters"]
            for field in required_func_fields:
                if field not in func_schema:
                    result.add_error(f"function.{field}", f"Required function field '{field}' is missing")

    def _validate_cohere_format(self,
                              schema: Dict[str, Any],
                              result: ValidationResult):
        """Validate Cohere-specific format"""
        if "parameter_definitions" in schema:
            param_defs = schema["parameter_definitions"]
            if not isinstance(param_defs, dict):
                result.add_error("parameter_definitions", "Cohere parameter_definitions must be a JSON object")
            else:
                for param_name, param_def in param_defs.items():
                    if not isinstance(param_def, dict):
                        result.add_error(f"parameter_definitions.{param_name}", "Parameter definition must be a JSON object")
                    elif "type" not in param_def:
                        result.add_error(f"parameter_definitions.{param_name}", "Parameter must have a 'type' field")

    def _validate_gemini_format(self,
                              schema: Dict[str, Any],
                              rules: Dict[str, Any],
                              result: ValidationResult):
        """Validate Gemini-specific format"""
        if rules.get("uses_openapi_schema"):
            # Add OpenAPI-specific validations if needed
            pass

class BatchValidator:
    """Validator for multiple schemas"""

    def __init__(self):
        self.validator = SchemaValidator()

    def validate_batch(self,
                      schemas: List[Tuple[Dict[str, Any], str]],
                      strict: bool = False) -> List[ValidationResult]:
        """
        Validate multiple schemas

        Args:
            schemas: List of (schema, provider) tuples
            strict: Whether to treat warnings as errors

        Returns:
            List of ValidationResult objects
        """
        results = []
        for schema, provider in schemas:
            result = self.validator.validate(schema, provider, strict)
            results.append(result)
        return results

    def get_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Get validation summary for batch results"""
        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        total_errors = sum(len(r.errors) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)

        return {
            "total_schemas": total,
            "valid_schemas": valid,
            "invalid_schemas": total - valid,
            "success_rate": (valid / total * 100) if total > 0 else 0,
            "total_errors": total_errors,
            "total_warnings": total_warnings
        }

# Global validator instance
validator = SchemaValidator()
batch_validator = BatchValidator()