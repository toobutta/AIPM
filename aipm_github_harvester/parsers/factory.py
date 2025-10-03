"""Parser factory for different file types."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..core.models import AIToolMetadata


class BaseParser(ABC):
    """Base class for all file parsers."""
    
    @abstractmethod
    def can_parse(self, file_path: str, content: str) -> bool:
        """Check if this parser can handle the given file."""
        pass
    
    @abstractmethod
    def parse(self, content: str, file_path: str) -> List[AIToolMetadata]:
        """Parse content and return extracted metadata."""
        pass


class ParserFactory:
    """Factory for creating appropriate parsers based on file type."""
    
    def __init__(self) -> None:
        self._parsers: Dict[str, BaseParser] = {}
        self._register_default_parsers()
    
    def _register_default_parsers(self) -> None:
        """Register default parsers for common file types."""
        from .readme_parser import ReadmeParser
        from .openapi_parser import OpenAPIParser
        from .mcp_parser import MCPParser
        from .python_parser import PythonParser
        from .markdown_parser import MarkdownParser
        
        parsers = [
            ReadmeParser(),
            OpenAPIParser(), 
            MCPParser(),
            PythonParser(),
            MarkdownParser(),
        ]
        
        for parser in parsers:
            self.register_parser(parser.__class__.__name__.lower().replace('parser', ''), parser)
    
    def register_parser(self, file_type: str, parser: BaseParser) -> None:
        """Register a parser for a specific file type."""
        self._parsers[file_type] = parser
    
    def get_parser(self, file_type: str) -> Optional[BaseParser]:
        """Get parser for the specified file type."""
        # Direct lookup first
        if file_type in self._parsers:
            return self._parsers[file_type]
        
        # Fallback mappings
        type_mappings = {
            'readme': 'readme',
            'markdown': 'markdown', 
            'openapi': 'openapi',
            'mcp': 'mcp',
            'python': 'python',
            'documentation': 'markdown',
            'config': 'openapi',  # Try OpenAPI parser for JSON/YAML configs
            'tools': 'python',  # Assume tools are Python for now
            'javascript': 'markdown',  # Parse as markdown for now
            'unknown': 'markdown',  # Default fallback
        }
        
        mapped_type = type_mappings.get(file_type)
        if mapped_type and mapped_type in self._parsers:
            return self._parsers[mapped_type]
        
        return None
    
    def get_all_parsers(self) -> Dict[str, BaseParser]:
        """Get all registered parsers."""
        return self._parsers.copy()