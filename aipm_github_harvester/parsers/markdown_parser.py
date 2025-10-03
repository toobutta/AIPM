"""Markdown file parser for extracting AI tool metadata."""

import re
from typing import List, Optional
import logging

from .readme_parser import ReadmeParser

logger = logging.getLogger(__name__)


class MarkdownParser(ReadmeParser):
    """Parser for Markdown files, extending README parser functionality."""
    
    def can_parse(self, file_path: str, content: str) -> bool:
        """Check if this parser can handle the given file."""
        return file_path.lower().endswith('.md')
    
    def parse(self, content: str, file_path: str) -> List:
        """Parse Markdown content and extract metadata."""
        # Use parent README parser logic but adapt for general markdown
        tools = super().parse(content, file_path)
        
        # Update extraction method
        for tool in tools:
            tool.extraction_method = ["markdown_parser"]
            tool.discovered_from = [file_path]
        
        return tools
    
    def _extract_project_name(self, content: str, file_path: str) -> Optional[str]:
        """Extract project name from markdown file."""
        # First try the parent method
        name = super()._extract_project_name(content, file_path)
        if name:
            return name
        
        # Try to get name from file path for non-README files
        file_name = file_path.split('/')[-1]
        if file_name.lower().endswith('.md'):
            name = file_name[:-3]
            if name and len(name) > 1:
                return name.replace('_', '-').replace(' ', '-')
        
        return None