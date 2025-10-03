"""MCP (Model Context Protocol) configuration parser."""

import json
import yaml
from typing import List, Dict, Any, Optional
import logging

from .factory import BaseParser
from ..core.models import (
    AIToolMetadata,
    FunctionDefinition, 
    FunctionParameter,
    InvocationParadigm,
    Protocol,
    SchemaType
)

logger = logging.getLogger(__name__)


class MCPParser(BaseParser):
    """Parser for MCP (Model Context Protocol) configuration files."""
    
    def can_parse(self, file_path: str, content: str) -> bool:
        """Check if this parser can handle the given file."""
        file_path_lower = file_path.lower()
        
        # Check if file is in MCP directory or has MCP in name
        if 'mcp' in file_path_lower:
            return True
        
        # Check content for MCP indicators
        try:
            if file_path_lower.endswith('.json'):
                data = json.loads(content)
            elif file_path_lower.endswith(('.yaml', '.yml')):
                data = yaml.safe_load(content)
            else:
                return False
            
            if isinstance(data, dict):
                # Look for MCP-specific fields
                return any(key in data for key in [
                    'tools', 'functions', 'mcp_version', 'protocol',
                    'capabilities', 'resources', 'prompts'
                ])
        
        except (json.JSONDecodeError, yaml.YAMLError):
            pass
        
        return False
    
    def parse(self, content: str, file_path: str) -> List[AIToolMetadata]:
        """Parse MCP content and extract metadata."""
        tools = []
        
        try:
            # Parse JSON or YAML
            if file_path.lower().endswith('.json'):
                config = json.loads(content)
            else:
                config = yaml.safe_load(content)
            
            if not isinstance(config, dict):
                return tools
            
            # Extract basic info
            tool_name = config.get('name', 'MCP Tool')
            description = config.get('description', 'MCP-based AI tool')
            version = config.get('version', config.get('mcp_version'))
            
            # Create base metadata
            tool = AIToolMetadata(
                name=tool_name,
                description=description,
                version=version,
                repository_url=None,  # Will be filled by harvester
                discovered_from=[file_path],
                extraction_method=["mcp_parser"],
                invocation_paradigm=[InvocationParadigm.FUNCTION_CALL],
                protocol=[Protocol.MCP],
                schema_type=SchemaType.JSON_SCHEMA
            )
            
            # Extract functions/tools
            functions = []
            
            # Check for 'tools' field (common MCP pattern)
            if 'tools' in config:
                functions.extend(self._extract_tools(config['tools']))
            
            # Check for 'functions' field
            if 'functions' in config:
                functions.extend(self._extract_functions(config['functions']))
            
            # Check for 'resources' field (MCP resources)
            if 'resources' in config:
                functions.extend(self._extract_resources(config['resources']))
            
            # Check for 'prompts' field (MCP prompts)
            if 'prompts' in config:
                functions.extend(self._extract_prompts(config['prompts']))
            
            tool.functions = functions
            
            # Extract capabilities
            capabilities = config.get('capabilities', {})
            if isinstance(capabilities, dict):
                # Add capabilities as tags
                tool.tags.extend(capabilities.keys())
                
                # Check for specific capability patterns
                if 'resources' in capabilities:
                    tool.tags.append('resource-access')
                if 'tools' in capabilities:
                    tool.tags.append('tool-calling')
                if 'prompts' in capabilities:
                    tool.tags.append('prompt-templates')
            
            # Extract model requirements
            if 'models' in config:
                models = config['models']
                if isinstance(models, list):
                    tool.compatible_models = models
                elif isinstance(models, str):
                    tool.model = models
            
            # Add MCP-specific tags
            tool.tags.extend(['mcp', 'ai-tool'])
            
            # Set confidence score
            tool.confidence_score = self._calculate_confidence(tool, config)
            
            tools.append(tool)
            
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            logger.error(f"Error parsing MCP config {file_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error parsing MCP config {file_path}: {e}")
        
        return tools
    
    def _extract_tools(self, tools_config: Any) -> List[FunctionDefinition]:
        """Extract tool definitions from MCP tools configuration."""
        functions = []
        
        if isinstance(tools_config, dict):
            for tool_name, tool_spec in tools_config.items():
                func = self._create_function_from_tool_spec(tool_name, tool_spec)
                if func:
                    functions.append(func)
        elif isinstance(tools_config, list):
            for tool_spec in tools_config:
                if isinstance(tool_spec, dict) and 'name' in tool_spec:
                    func = self._create_function_from_tool_spec(tool_spec['name'], tool_spec)
                    if func:
                        functions.append(func)
        
        return functions
    
    def _extract_functions(self, functions_config: Any) -> List[FunctionDefinition]:
        """Extract function definitions from MCP functions configuration."""
        functions = []
        
        if isinstance(functions_config, dict):
            for func_name, func_spec in functions_config.items():
                func = self._create_function_from_spec(func_name, func_spec)
                if func:
                    functions.append(func)
        elif isinstance(functions_config, list):
            for func_spec in functions_config:
                if isinstance(func_spec, dict) and 'name' in func_spec:
                    func = self._create_function_from_spec(func_spec['name'], func_spec)
                    if func:
                        functions.append(func)
        
        return functions
    
    def _extract_resources(self, resources_config: Any) -> List[FunctionDefinition]:
        """Extract resource definitions as functions."""
        functions = []
        
        if isinstance(resources_config, dict):
            for resource_name, resource_spec in resources_config.items():
                func = FunctionDefinition(
                    name=f"access_{resource_name}",
                    description=f"Access MCP resource: {resource_name}",
                    tags=['resource', 'mcp']
                )
                functions.append(func)
        elif isinstance(resources_config, list):
            for resource in resources_config:
                if isinstance(resource, dict) and 'name' in resource:
                    func = FunctionDefinition(
                        name=f"access_{resource['name']}",
                        description=resource.get('description', f"Access MCP resource: {resource['name']}"),
                        tags=['resource', 'mcp']
                    )
                    functions.append(func)
                elif isinstance(resource, str):
                    func = FunctionDefinition(
                        name=f"access_{resource}",
                        description=f"Access MCP resource: {resource}",
                        tags=['resource', 'mcp']
                    )
                    functions.append(func)
        
        return functions
    
    def _extract_prompts(self, prompts_config: Any) -> List[FunctionDefinition]:
        """Extract prompt templates as functions."""
        functions = []
        
        if isinstance(prompts_config, dict):
            for prompt_name, prompt_spec in prompts_config.items():
                description = "MCP prompt template"
                if isinstance(prompt_spec, dict):
                    description = prompt_spec.get('description', description)
                
                func = FunctionDefinition(
                    name=f"prompt_{prompt_name}",
                    description=description,
                    tags=['prompt', 'template', 'mcp']
                )
                functions.append(func)
        elif isinstance(prompts_config, list):
            for prompt in prompts_config:
                if isinstance(prompt, dict) and 'name' in prompt:
                    func = FunctionDefinition(
                        name=f"prompt_{prompt['name']}",
                        description=prompt.get('description', 'MCP prompt template'),
                        tags=['prompt', 'template', 'mcp']
                    )
                    functions.append(func)
        
        return functions
    
    def _create_function_from_tool_spec(self, name: str, spec: Any) -> Optional[FunctionDefinition]:
        """Create function from MCP tool specification."""
        try:
            if isinstance(spec, dict):
                description = spec.get('description', f'MCP tool: {name}')
                
                # Extract parameters
                parameters = []
                if 'parameters' in spec:
                    params_spec = spec['parameters']
                    if isinstance(params_spec, dict):
                        if 'properties' in params_spec:
                            # JSON Schema style
                            properties = params_spec['properties']
                            required_fields = params_spec.get('required', [])
                            
                            for param_name, param_spec in properties.items():
                                if isinstance(param_spec, dict):
                                    param = FunctionParameter(
                                        name=param_name,
                                        type=param_spec.get('type', 'string'),
                                        description=param_spec.get('description', ''),
                                        required=param_name in required_fields,
                                        param_schema=param_spec
                                    )
                                    parameters.append(param)
                
                func = FunctionDefinition(
                    name=name,
                    description=description,
                    parameters=parameters,
                    tags=['tool', 'mcp']
                )
                
                return func
            else:
                # Simple string specification
                return FunctionDefinition(
                    name=name,
                    description=f'MCP tool: {name}',
                    tags=['tool', 'mcp']
                )
                
        except Exception as e:
            logger.warning(f"Error creating function from tool spec {name}: {e}")
            return None
    
    def _create_function_from_spec(self, name: str, spec: Any) -> Optional[FunctionDefinition]:
        """Create function from generic specification."""
        try:
            description = f'MCP function: {name}'
            parameters = []
            
            if isinstance(spec, dict):
                description = spec.get('description', description)
                
                # Extract parameters if available
                if 'parameters' in spec or 'args' in spec:
                    param_spec = spec.get('parameters', spec.get('args', {}))
                    if isinstance(param_spec, dict):
                        for param_name, param_info in param_spec.items():
                            param_type = 'string'
                            param_desc = ''
                            required = False
                            
                            if isinstance(param_info, dict):
                                param_type = param_info.get('type', 'string')
                                param_desc = param_info.get('description', '')
                                required = param_info.get('required', False)
                            
                            param = FunctionParameter(
                                name=param_name,
                                type=param_type,
                                description=param_desc,
                                required=required
                            )
                            parameters.append(param)
            
            return FunctionDefinition(
                name=name,
                description=description,
                parameters=parameters,
                tags=['function', 'mcp']
            )
            
        except Exception as e:
            logger.warning(f"Error creating function from spec {name}: {e}")
            return None
    
    def _calculate_confidence(self, tool: AIToolMetadata, config: Dict[str, Any]) -> float:
        """Calculate confidence score based on MCP configuration completeness."""
        score = 0.6  # Base score for having MCP config
        
        if tool.functions:
            score += 0.2
        if config.get('capabilities'):
            score += 0.1
        if config.get('description'):
            score += 0.05
        if config.get('version') or config.get('mcp_version'):
            score += 0.05
        
        return min(1.0, score)