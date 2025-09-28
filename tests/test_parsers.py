"""Tests for parser functionality."""

import json
import pytest

from aipm_github_harvester.parsers.readme_parser import ReadmeParser
from aipm_github_harvester.parsers.openapi_parser import OpenAPIParser
from aipm_github_harvester.parsers.mcp_parser import MCPParser
from aipm_github_harvester.parsers.factory import ParserFactory


class TestReadmeParser:
    """Tests for README parser."""
    
    def test_can_parse_readme(self):
        """Test README file detection."""
        parser = ReadmeParser()
        
        assert parser.can_parse("README.md", "")
        assert parser.can_parse("readme.txt", "")
        assert not parser.can_parse("main.py", "")
    
    def test_parse_readme_content(self, sample_readme_content):
        """Test parsing README content."""
        parser = ReadmeParser()
        
        tools = parser.parse(sample_readme_content, "README.md")
        
        assert len(tools) == 1
        tool = tools[0]
        
        assert "Test AI Tool" in tool.name
        assert "test AI tool" in tool.description.lower()
        assert "api" in [p.value for p in tool.invocation_paradigm]
        assert "sdk" in [p.value for p in tool.invocation_paradigm]
        assert len(tool.functions) > 0


class TestOpenAPIParser:
    """Tests for OpenAPI parser."""
    
    def test_can_parse_openapi_json(self):
        """Test OpenAPI JSON file detection."""
        parser = OpenAPIParser()
        
        assert parser.can_parse("openapi.json", '{"openapi": "3.0.0"}')
        assert parser.can_parse("swagger.yaml", 'openapi: 3.0.0')
        assert not parser.can_parse("data.json", '{"data": "test"}')
    
    def test_parse_openapi_spec(self, sample_openapi_spec):
        """Test parsing OpenAPI specification."""
        parser = OpenAPIParser()
        content = json.dumps(sample_openapi_spec)
        
        tools = parser.parse(content, "openapi.json")
        
        assert len(tools) == 1
        tool = tools[0]
        
        assert tool.name == "Test API"
        assert "test API" in tool.description.lower()
        assert "api" in [p.value for p in tool.invocation_paradigm]
        assert "openapi" in [p.value for p in tool.protocol]
        assert len(tool.functions) == 1
        
        func = tool.functions[0]
        assert func.name == "generate_text"
        assert len(func.parameters) == 2  # prompt and max_tokens


class TestMCPParser:
    """Tests for MCP parser."""
    
    def test_can_parse_mcp_config(self):
        """Test MCP configuration detection."""
        parser = MCPParser()
        
        assert parser.can_parse("mcp/config.json", '{"tools": {}}')
        assert parser.can_parse("mcp.yaml", 'capabilities: {}')
        assert not parser.can_parse("config.json", '{"other": "data"}')
    
    def test_parse_mcp_config(self, sample_mcp_config):
        """Test parsing MCP configuration."""
        parser = MCPParser()
        content = json.dumps(sample_mcp_config)
        
        tools = parser.parse(content, "mcp/config.json")
        
        assert len(tools) == 1
        tool = tools[0]
        
        assert tool.name == "test-mcp-tool"
        assert "test MCP tool" in tool.description
        assert "function_call" in [p.value for p in tool.invocation_paradigm]
        assert "mcp" in [p.value for p in tool.protocol]
        assert len(tool.functions) == 1
        
        func = tool.functions[0]
        assert func.name == "search_web"
        assert len(func.parameters) == 2  # query and limit


class TestParserFactory:
    """Tests for parser factory."""
    
    def test_get_parser_by_type(self):
        """Test getting parsers by file type."""
        factory = ParserFactory()
        
        readme_parser = factory.get_parser("readme")
        assert isinstance(readme_parser, ReadmeParser)
        
        openapi_parser = factory.get_parser("openapi")
        assert isinstance(openapi_parser, OpenAPIParser)
        
        mcp_parser = factory.get_parser("mcp")
        assert isinstance(mcp_parser, MCPParser)
    
    def test_get_parser_fallback(self):
        """Test parser fallback for unknown types."""
        factory = ParserFactory()
        
        # Should fall back to markdown parser for unknown types
        parser = factory.get_parser("unknown")
        assert parser is not None
    
    def test_get_all_parsers(self):
        """Test getting all registered parsers."""
        factory = ParserFactory()
        
        parsers = factory.get_all_parsers()
        
        assert len(parsers) > 0
        assert "readme" in parsers
        assert "openapi" in parsers
        assert "mcp" in parsers