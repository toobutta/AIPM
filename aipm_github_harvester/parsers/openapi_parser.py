"""OpenAPI specification parser."""

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


class OpenAPIParser(BaseParser):
    """Parser for OpenAPI/Swagger specification files."""
    
    def can_parse(self, file_path: str, content: str) -> bool:
        """Check if this parser can handle the given file."""
        file_path_lower = file_path.lower()
        
        # Check file path indicators
        if any(indicator in file_path_lower for indicator in ['openapi', 'swagger']):
            return True
        
        # Check content for OpenAPI indicators
        try:
            if file_path_lower.endswith('.json'):
                data = json.loads(content)
            elif file_path_lower.endswith(('.yaml', '.yml')):
                data = yaml.safe_load(content)
            else:
                return False
            
            # Check for OpenAPI/Swagger indicators in content
            if isinstance(data, dict):
                return any(key in data for key in ['openapi', 'swagger', 'info', 'paths'])
        
        except (json.JSONDecodeError, yaml.YAMLError):
            pass
        
        return False
    
    def parse(self, content: str, file_path: str) -> List[AIToolMetadata]:
        """Parse OpenAPI content and extract metadata."""
        tools = []
        
        try:
            # Parse JSON or YAML
            if file_path.lower().endswith('.json'):
                spec = json.loads(content)
            else:
                spec = yaml.safe_load(content)
            
            if not isinstance(spec, dict):
                return tools
            
            # Extract basic info
            info = spec.get('info', {})
            tool_name = info.get('title', 'Unknown API')
            description = info.get('description')
            version = info.get('version')
            
            # Create base metadata
            tool = AIToolMetadata(
                name=tool_name,
                description=description,
                version=version,
                repository_url=None,  # Will be filled by harvester
                discovered_from=[file_path],
                extraction_method=["openapi_parser"],
                invocation_paradigm=[InvocationParadigm.API],
                protocol=[Protocol.HTTP, Protocol.REST, Protocol.OPENAPI],
                schema_type=SchemaType.OPENAPI
            )
            
            # Extract server information
            servers = spec.get('servers', [])
            if servers and isinstance(servers, list) and servers[0].get('url'):
                try:
                    tool.api_endpoint = servers[0]['url']
                except:
                    pass
            
            # Extract functions from paths
            paths = spec.get('paths', {})
            tool.functions = self._extract_functions_from_paths(paths, spec)
            
            # Extract schemas
            components = spec.get('components', {})
            schemas = components.get('schemas', {})
            if schemas:
                tool.args_schema = schemas
            
            # Extract tags and categories
            if 'tags' in spec:
                tool.tags = [tag.get('name', '') for tag in spec['tags'] if isinstance(tag, dict)]
            
            # Set confidence score
            tool.confidence_score = self._calculate_confidence(tool, spec)
            
            tools.append(tool)
            
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            logger.error(f"Error parsing OpenAPI spec {file_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error parsing OpenAPI spec {file_path}: {e}")
        
        return tools
    
    def _extract_functions_from_paths(self, paths: Dict[str, Any], spec: Dict[str, Any]) -> List[FunctionDefinition]:
        """Extract function definitions from OpenAPI paths."""
        functions = []
        
        for path, path_data in paths.items():
            if not isinstance(path_data, dict):
                continue
                
            for method, operation in path_data.items():
                if method in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head'] and isinstance(operation, dict):
                    func = self._create_function_from_operation(path, method, operation, spec)
                    if func:
                        functions.append(func)
        
        return functions
    
    def _create_function_from_operation(
        self, 
        path: str, 
        method: str, 
        operation: Dict[str, Any], 
        spec: Dict[str, Any]
    ) -> Optional[FunctionDefinition]:
        """Create function definition from OpenAPI operation."""
        try:
            # Generate function name
            operation_id = operation.get('operationId')
            if operation_id:
                func_name = operation_id
            else:
                # Generate name from path and method
                path_parts = [part for part in path.split('/') if part and not part.startswith('{')]
                func_name = f"{method}_{('_'.join(path_parts) if path_parts else 'root')}"
            
            # Get description
            summary = operation.get('summary', '')
            description = operation.get('description', summary)
            
            # Extract parameters
            parameters = []
            
            # Path parameters
            path_params = operation.get('parameters', [])
            for param in path_params:
                if isinstance(param, dict):
                    param_obj = self._create_parameter_from_spec(param, spec)
                    if param_obj:
                        parameters.append(param_obj)
            
            # Request body parameters (for POST/PUT/PATCH)
            request_body = operation.get('requestBody', {})
            if request_body and isinstance(request_body, dict):
                body_params = self._extract_body_parameters(request_body, spec)
                parameters.extend(body_params)
            
            # Create function definition
            func = FunctionDefinition(
                name=func_name,
                description=description if description else f"{method.upper()} {path}",
                parameters=parameters
            )
            
            # Extract response schema
            responses = operation.get('responses', {})
            if '200' in responses:
                success_response = responses['200']
                if isinstance(success_response, dict):
                    content = success_response.get('content', {})
                    if 'application/json' in content:
                        schema = content['application/json'].get('schema')
                        if schema:
                            func.return_schema = schema
            
            # Add tags
            if 'tags' in operation:
                func.tags = operation['tags']
            
            return func
            
        except Exception as e:
            logger.warning(f"Error creating function for {method} {path}: {e}")
            return None
    
    def _create_parameter_from_spec(self, param_spec: Dict[str, Any], spec: Dict[str, Any]) -> Optional[FunctionParameter]:
        """Create parameter object from OpenAPI parameter specification."""
        try:
            name = param_spec.get('name', '')
            if not name:
                return None
            
            description = param_spec.get('description', '')
            required = param_spec.get('required', False)
            
            # Get parameter type
            param_type = 'string'  # default
            schema = param_spec.get('schema', {})
            if isinstance(schema, dict):
                param_type = schema.get('type', 'string')
                
                # Handle array types
                if param_type == 'array':
                    items = schema.get('items', {})
                    if isinstance(items, dict):
                        item_type = items.get('type', 'string')
                        param_type = f"array[{item_type}]"
            
            return FunctionParameter(
                name=name,
                type=param_type,
                description=description,
                required=required,
                param_schema=schema if schema else None
            )
            
        except Exception as e:
            logger.warning(f"Error creating parameter from spec: {e}")
            return None
    
    def _extract_body_parameters(self, request_body: Dict[str, Any], spec: Dict[str, Any]) -> List[FunctionParameter]:
        """Extract parameters from request body specification."""
        parameters = []
        
        try:
            content = request_body.get('content', {})
            for media_type, media_spec in content.items():
                if not isinstance(media_spec, dict):
                    continue
                    
                schema = media_spec.get('schema', {})
                if not isinstance(schema, dict):
                    continue
                
                # Handle object schemas with properties
                if schema.get('type') == 'object':
                    properties = schema.get('properties', {})
                    required_fields = schema.get('required', [])
                    
                    for prop_name, prop_spec in properties.items():
                        if isinstance(prop_spec, dict):
                            param = FunctionParameter(
                                name=prop_name,
                                type=prop_spec.get('type', 'string'),
                                description=prop_spec.get('description', ''),
                                required=prop_name in required_fields,
                                param_schema=prop_spec
                            )
                            parameters.append(param)
                else:
                    # Handle primitive request body
                    param = FunctionParameter(
                        name='body',
                        type=schema.get('type', 'object'),
                        description=request_body.get('description', 'Request body'),
                        required=request_body.get('required', True),
                        param_schema=schema
                    )
                    parameters.append(param)
                
                break  # Just process the first media type
                
        except Exception as e:
            logger.warning(f"Error extracting body parameters: {e}")
        
        return parameters
    
    def _calculate_confidence(self, tool: AIToolMetadata, spec: Dict[str, Any]) -> float:
        """Calculate confidence score based on OpenAPI specification completeness."""
        score = 0.5  # Base score for having OpenAPI spec
        
        if tool.name and tool.name != 'Unknown API':
            score += 0.1
        if tool.description:
            score += 0.1
        if tool.functions:
            score += 0.2
        if spec.get('paths'):
            score += 0.1
        if spec.get('components', {}).get('schemas'):
            score += 0.1
        
        return min(1.0, score)