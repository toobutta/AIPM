"""Tests for core models and functionality."""

import pytest
from datetime import datetime

from aipm_github_harvester.core.models import (
    AIToolMetadata,
    FunctionDefinition,
    FunctionParameter,
    HarvestConfig,
    InvocationParadigm,
    Protocol,
    SchemaType,
)


def test_function_parameter_creation():
    """Test FunctionParameter model creation."""
    param = FunctionParameter(
        name="test_param",
        type="string",
        description="A test parameter",
        required=True,
        param_schema={"type": "string", "maxLength": 100}
    )
    
    assert param.name == "test_param"
    assert param.type == "string"
    assert param.description == "A test parameter"
    assert param.required is True
    assert param.param_schema == {"type": "string", "maxLength": 100}


def test_function_definition_creation():
    """Test FunctionDefinition model creation."""
    param1 = FunctionParameter(name="param1", type="string", required=True)
    param2 = FunctionParameter(name="param2", type="integer", required=False)
    
    func = FunctionDefinition(
        name="test_function",
        description="A test function",
        parameters=[param1, param2],
        return_type="string",
        tags=["test", "example"]
    )
    
    assert func.name == "test_function"
    assert func.description == "A test function"
    assert len(func.parameters) == 2
    assert func.return_type == "string"
    assert "test" in func.tags


def test_ai_tool_metadata_creation():
    """Test AIToolMetadata model creation."""
    func = FunctionDefinition(name="test_func", description="Test function")
    
    tool = AIToolMetadata(
        name="Test Tool",
        description="A test AI tool",
        repository_url="https://github.com/test/repo",
        functions=[func],
        invocation_paradigm=[InvocationParadigm.API],
        protocol=[Protocol.HTTP],
        provider="test-provider"
    )
    
    assert tool.name == "Test Tool"
    assert tool.description == "A test AI tool"
    assert len(tool.functions) == 1
    assert InvocationParadigm.API in tool.invocation_paradigm
    assert Protocol.HTTP in tool.protocol
    assert tool.provider == "test-provider"
    assert isinstance(tool.extracted_at, datetime)


def test_harvest_config_defaults():
    """Test HarvestConfig default values."""
    config = HarvestConfig()
    
    assert config.clone_depth == 1
    assert config.max_file_size_mb == 10
    assert "README*" in config.include_patterns
    assert ".git/**" in config.exclude_patterns
    assert "jsonl" in config.output_formats
    assert config.parallel_processing is True
    assert config.max_workers == 4


def test_harvest_config_custom():
    """Test HarvestConfig with custom values."""
    config = HarvestConfig(
        clone_depth=5,
        max_file_size_mb=20,
        parallel_processing=False,
        max_workers=2,
        output_formats=["csv"]
    )
    
    assert config.clone_depth == 5
    assert config.max_file_size_mb == 20
    assert config.parallel_processing is False
    assert config.max_workers == 2
    assert config.output_formats == ["csv"]


def test_invocation_paradigm_enum():
    """Test InvocationParadigm enum values."""
    assert InvocationParadigm.API == "api"
    assert InvocationParadigm.CLI == "cli"
    assert InvocationParadigm.SDK == "sdk"
    assert InvocationParadigm.FUNCTION_CALL == "function_call"


def test_protocol_enum():
    """Test Protocol enum values."""
    assert Protocol.HTTP == "http"
    assert Protocol.HTTPS == "https"
    assert Protocol.REST == "rest"
    assert Protocol.OPENAPI == "openapi"
    assert Protocol.MCP == "mcp"


def test_schema_type_enum():
    """Test SchemaType enum values."""
    assert SchemaType.JSON_SCHEMA == "json_schema"
    assert SchemaType.OPENAPI == "openapi"
    assert SchemaType.PYDANTIC == "pydantic"