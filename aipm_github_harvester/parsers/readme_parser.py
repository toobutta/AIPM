"""README file parser."""

import re
from typing import List, Optional, Dict, Any
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


class ReadmeParser(BaseParser):
    """Parser for README files to extract AI tool metadata."""
    
    def can_parse(self, file_path: str, content: str) -> bool:
        """Check if this parser can handle the given file."""
        return file_path.lower().startswith('readme')
    
    def parse(self, content: str, file_path: str) -> List[AIToolMetadata]:
        """Parse README content and extract metadata."""
        tools = []
        
        try:
            # Extract basic project info
            tool_name = self._extract_project_name(content, file_path)
            description = self._extract_description(content)
            
            if not tool_name:
                return tools
            
            # Create base metadata
            tool = AIToolMetadata(
                name=tool_name,
                description=description,
                repository_url=None,  # Will be filled by harvester
                discovered_from=[file_path],
                extraction_method=["readme_parser"]
            )
            
            # Extract invocation paradigms
            tool.invocation_paradigm = self._extract_invocation_paradigms(content)
            
            # Extract protocols
            tool.protocol = self._extract_protocols(content)
            
            # Extract functions from code examples
            tool.functions = self._extract_functions_from_examples(content)
            
            # Extract model information
            tool.model = self._extract_model_info(content)
            
            # Extract tags and categories
            tool.tags = self._extract_tags(content)
            tool.categories = self._extract_categories(content)
            
            # Set confidence based on extracted info
            tool.confidence_score = self._calculate_confidence(tool)
            
            tools.append(tool)
            
        except Exception as e:
            logger.error(f"Error parsing README {file_path}: {e}")
        
        return tools
    
    def _extract_project_name(self, content: str, file_path: str) -> Optional[str]:
        """Extract project name from README."""
        # Try to find main heading
        lines = content.split('\n')
        
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            
            # Look for markdown headings
            if line.startswith('# '):
                name = line[2:].strip()
                # Clean up common patterns
                name = re.sub(r'\[.*?\]\(.*?\)', '', name)  # Remove links
                name = re.sub(r'[^\w\s\-_]', '', name)  # Remove special chars
                if name and len(name) > 1:
                    return name
        
        # Fallback to file path based name
        return None
    
    def _extract_description(self, content: str) -> Optional[str]:
        """Extract project description."""
        lines = content.split('\n')
        
        # Look for description after title
        found_title = False
        for line in lines:
            line = line.strip()
            
            if line.startswith('# '):
                found_title = True
                continue
            
            if found_title and line and not line.startswith('#'):
                # Clean up the description
                desc = re.sub(r'\[.*?\]\(.*?\)', '', line)  # Remove links
                desc = re.sub(r'[*_`]', '', desc)  # Remove markdown formatting
                desc = desc.strip()
                if len(desc) > 10:
                    return desc
        
        return None
    
    def _extract_invocation_paradigms(self, content: str) -> List[InvocationParadigm]:
        """Extract invocation paradigms from content."""
        paradigms = []
        content_lower = content.lower()
        
        # Look for keywords that indicate paradigms
        if any(word in content_lower for word in ['api', 'endpoint', 'rest', 'http']):
            paradigms.append(InvocationParadigm.API)
        
        if any(word in content_lower for word in ['cli', 'command line', 'terminal']):
            paradigms.append(InvocationParadigm.CLI)
        
        if any(word in content_lower for word in ['sdk', 'library', 'import', 'install']):
            paradigms.append(InvocationParadigm.SDK)
        
        if any(word in content_lower for word in ['webhook', 'callback']):
            paradigms.append(InvocationParadigm.WEBHOOK)
        
        if any(word in content_lower for word in ['function', 'call', 'invoke']):
            paradigms.append(InvocationParadigm.FUNCTION_CALL)
        
        if any(word in content_lower for word in ['plugin', 'extension']):
            paradigms.append(InvocationParadigm.PLUGIN)
        
        return list(set(paradigms))  # Remove duplicates
    
    def _extract_protocols(self, content: str) -> List[Protocol]:
        """Extract communication protocols from content."""
        protocols = []
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['http://', 'https://', 'rest', 'restful']):
            protocols.append(Protocol.HTTP)
        
        if 'grpc' in content_lower:
            protocols.append(Protocol.GRPC)
        
        if any(word in content_lower for word in ['websocket', 'ws://', 'wss://']):
            protocols.append(Protocol.WEBSOCKET)
        
        if 'graphql' in content_lower:
            protocols.append(Protocol.GRAPHQL)
        
        if any(word in content_lower for word in ['openapi', 'swagger']):
            protocols.append(Protocol.OPENAPI)
        
        if 'mcp' in content_lower:
            protocols.append(Protocol.MCP)
        
        return list(set(protocols))
    
    def _extract_functions_from_examples(self, content: str) -> List[FunctionDefinition]:
        """Extract function definitions from code examples."""
        functions = []
        
        # Look for code blocks
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
        
        for block in code_blocks:
            # Look for function-like patterns
            func_patterns = [
                r'def\s+(\w+)\s*\(',  # Python functions
                r'function\s+(\w+)\s*\(',  # JavaScript functions  
                r'(\w+)\s*\(',  # Generic function calls
            ]
            
            for pattern in func_patterns:
                matches = re.findall(pattern, block)
                for match in matches:
                    if len(match) > 2 and not match.startswith('_'):
                        func = FunctionDefinition(
                            name=match,
                            description=f"Function extracted from README example"
                        )
                        functions.append(func)
        
        return functions[:5]  # Limit to first 5 functions
    
    def _extract_model_info(self, content: str) -> Optional[str]:
        """Extract AI model information."""
        content_lower = content.lower()
        
        # Look for common AI model names
        models = ['gpt-4', 'gpt-3.5', 'claude', 'llama', 'palm', 'gemini', 'openai', 'anthropic']
        
        for model in models:
            if model in content_lower:
                return model
        
        return None
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from content."""
        tags = []
        content_lower = content.lower()
        
        # Common AI/tool related tags
        potential_tags = [
            'ai', 'ml', 'machine-learning', 'nlp', 'llm', 'chatbot', 'assistant',
            'api', 'sdk', 'cli', 'tool', 'automation', 'integration'
        ]
        
        for tag in potential_tags:
            if tag in content_lower:
                tags.append(tag)
        
        return tags
    
    def _extract_categories(self, content: str) -> List[str]:
        """Extract categories from content."""
        categories = []
        content_lower = content.lower()
        
        category_keywords = {
            'development': ['develop', 'code', 'programming', 'software'],
            'ai-assistant': ['assistant', 'chatbot', 'ai', 'llm'],
            'automation': ['automate', 'workflow', 'pipeline', 'cicd'],
            'data': ['data', 'analytics', 'database', 'processing'],
            'web': ['web', 'http', 'rest', 'api', 'service'],
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                categories.append(category)
        
        return categories
    
    def _calculate_confidence(self, tool: AIToolMetadata) -> float:
        """Calculate confidence score based on extracted information."""
        score = 0.0
        
        if tool.name:
            score += 0.3
        if tool.description:
            score += 0.2
        if tool.functions:
            score += 0.2
        if tool.invocation_paradigm:
            score += 0.1
        if tool.protocol:
            score += 0.1
        if tool.tags:
            score += 0.1
        
        return min(1.0, score)