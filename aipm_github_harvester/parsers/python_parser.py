"""Python file parser for extracting function definitions."""

import ast
import re
from typing import List, Optional
import logging

from .factory import BaseParser
from ..core.models import (
    AIToolMetadata,
    FunctionDefinition,
    FunctionParameter,
    InvocationParadigm,
    Protocol
)

logger = logging.getLogger(__name__)


class PythonParser(BaseParser):
    """Parser for Python files to extract function and class definitions."""
    
    def can_parse(self, file_path: str, content: str) -> bool:
        """Check if this parser can handle the given file."""
        return file_path.lower().endswith('.py')
    
    def parse(self, content: str, file_path: str) -> List[AIToolMetadata]:
        """Parse Python content and extract metadata."""
        tools = []
        
        try:
            # Try to parse as AST first
            try:
                tree = ast.parse(content)
                functions = self._extract_functions_from_ast(tree)
            except SyntaxError:
                # Fall back to regex parsing
                functions = self._extract_functions_from_regex(content)
            
            if functions:
                # Create tool metadata
                tool_name = self._extract_module_name(file_path, content)
                description = self._extract_module_description(content)
                
                tool = AIToolMetadata(
                    name=tool_name,
                    description=description,
                    repository_url=None,  # Will be filled by harvester
                    functions=functions,
                    discovered_from=[file_path],
                    extraction_method=["python_parser"],
                    invocation_paradigm=[InvocationParadigm.LIBRARY, InvocationParadigm.FUNCTION_CALL],
                    protocol=[Protocol.HTTP] if self._has_web_indicators(content) else [],
                    tags=self._extract_tags(content),
                    confidence_score=0.7
                )
                
                tools.append(tool)
                
        except Exception as e:
            logger.error(f"Error parsing Python file {file_path}: {e}")
        
        return tools
    
    def _extract_functions_from_ast(self, tree: ast.AST) -> List[FunctionDefinition]:
        """Extract function definitions using AST parsing."""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private functions
                if node.name.startswith('_'):
                    continue
                
                # Extract function info
                func = FunctionDefinition(
                    name=node.name,
                    description=ast.get_docstring(node) or f"Python function: {node.name}",
                    parameters=self._extract_parameters_from_ast(node)
                )
                
                functions.append(func)
        
        return functions
    
    def _extract_parameters_from_ast(self, func_node: ast.FunctionDef) -> List[FunctionParameter]:
        """Extract parameters from function AST node."""
        parameters = []
        
        # Regular arguments
        for arg in func_node.args.args:
            if arg.arg == 'self':
                continue
            
            param_type = 'Any'
            if arg.annotation:
                param_type = ast.unparse(arg.annotation) if hasattr(ast, 'unparse') else 'Any'
            
            param = FunctionParameter(
                name=arg.arg,
                type=param_type,
                required=True  # Will be updated below for defaults
            )
            parameters.append(param)
        
        # Handle defaults
        num_defaults = len(func_node.args.defaults)
        if num_defaults > 0:
            # Mark last num_defaults parameters as optional
            for i in range(len(parameters) - num_defaults, len(parameters)):
                if i >= 0:
                    parameters[i].required = False
        
        return parameters
    
    def _extract_functions_from_regex(self, content: str) -> List[FunctionDefinition]:
        """Extract function definitions using regex (fallback)."""
        functions = []
        
        # Find function definitions
        func_pattern = r'^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\):'
        matches = re.finditer(func_pattern, content, re.MULTILINE)
        
        for match in matches:
            func_name = match.group(1)
            
            # Skip private functions
            if func_name.startswith('_'):
                continue
            
            # Try to find docstring
            func_start = match.end()
            lines = content[func_start:].split('\n')
            
            description = f"Python function: {func_name}"
            for line in lines[1:4]:  # Check first few lines for docstring
                line = line.strip()
                if line.startswith('"""') or line.startswith("'''"):
                    # Extract docstring
                    quote_type = '"""' if line.startswith('"""') else "'''"
                    if line.count(quote_type) >= 2:
                        # Single line docstring
                        description = line.strip(quote_type).strip()
                    break
            
            func = FunctionDefinition(
                name=func_name,
                description=description
            )
            functions.append(func)
        
        return functions
    
    def _extract_module_name(self, file_path: str, content: str) -> str:
        """Extract module name from file path or content."""
        # Try to get name from file path
        file_name = file_path.split('/')[-1]
        if file_name.endswith('.py'):
            name = file_name[:-3]
            if name != '__init__':
                return name.replace('_', '-')
        
        # Look for __name__ or similar in content
        name_match = re.search(r'__name__\s*=\s*["\']([^"\']+)["\']', content)
        if name_match:
            return name_match.group(1)
        
        return 'python-module'
    
    def _extract_module_description(self, content: str) -> Optional[str]:
        """Extract module description from docstring."""
        lines = content.split('\n')
        
        # Look for module docstring at the top
        in_docstring = False
        docstring_lines = []
        quote_type = None
        
        for line in lines[:20]:  # Check first 20 lines
            line = line.strip()
            
            if not in_docstring:
                if line.startswith('"""') or line.startswith("'''"):
                    quote_type = '"""' if line.startswith('"""') else "'''"
                    in_docstring = True
                    
                    # Check if single-line docstring
                    content_after_start = line[3:]
                    if content_after_start.endswith(quote_type):
                        return content_after_start[:-3].strip()
                    else:
                        docstring_lines.append(content_after_start)
                elif line and not line.startswith('#') and not line.startswith('import'):
                    # Hit non-comment, non-import code without docstring
                    break
            else:
                if line.endswith(quote_type):
                    # End of docstring
                    docstring_lines.append(line[:-3])
                    return ' '.join(docstring_lines).strip()
                else:
                    docstring_lines.append(line)
        
        return None
    
    def _has_web_indicators(self, content: str) -> bool:
        """Check if content has web/HTTP indicators."""
        web_keywords = ['flask', 'django', 'fastapi', 'requests', 'http', 'api', 'server']
        content_lower = content.lower()
        
        return any(keyword in content_lower for keyword in web_keywords)
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from Python content."""
        tags = ['python']
        content_lower = content.lower()
        
        # Framework detection
        if any(fw in content_lower for fw in ['flask', 'django', 'fastapi']):
            tags.append('web-framework')
        
        if any(lib in content_lower for lib in ['requests', 'httpx', 'aiohttp']):
            tags.append('http-client')
        
        if any(ai in content_lower for ai in ['openai', 'anthropic', 'langchain', 'llama']):
            tags.append('ai-integration')
        
        return tags