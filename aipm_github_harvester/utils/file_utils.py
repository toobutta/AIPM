"""File system utilities for scanning and filtering files."""

import os
from pathlib import Path
from typing import List, Set
import fnmatch
import logging

logger = logging.getLogger(__name__)


class FileScanner:
    """Scanner for finding relevant files in repositories."""
    
    def __init__(
        self, 
        include_patterns: List[str], 
        exclude_patterns: List[str],
        max_file_size_mb: int = 10
    ) -> None:
        """Initialize file scanner with patterns."""
        self.include_patterns = include_patterns
        self.exclude_patterns = exclude_patterns
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
    
    def scan_directory(self, root_dir: str) -> List[Path]:
        """Scan directory for relevant files based on patterns."""
        relevant_files = []
        root_path = Path(root_dir)
        
        if not root_path.exists() or not root_path.is_dir():
            logger.error(f"Directory does not exist or is not a directory: {root_dir}")
            return relevant_files
        
        try:
            # Walk through all files
            for file_path in self._walk_directory(root_path):
                relative_path = file_path.relative_to(root_path)
                relative_str = str(relative_path)
                
                # Check if file should be excluded
                if self._should_exclude(relative_str):
                    continue
                
                # Check if file matches include patterns
                if self._should_include(relative_str):
                    # Check file size
                    if self._check_file_size(file_path):
                        relevant_files.append(file_path)
                        logger.debug(f"Found relevant file: {relative_str}")
                    else:
                        logger.warning(f"File too large, skipping: {relative_str}")
        
        except Exception as e:
            logger.error(f"Error scanning directory {root_dir}: {e}")
        
        logger.info(f"Found {len(relevant_files)} relevant files in {root_dir}")
        return relevant_files
    
    def _walk_directory(self, root_path: Path) -> List[Path]:
        """Walk directory and return all files."""
        files = []
        
        try:
            for item in root_path.rglob('*'):
                if item.is_file():
                    files.append(item)
        except (OSError, PermissionError) as e:
            logger.warning(f"Error accessing some files in {root_path}: {e}")
        
        return files
    
    def _should_include(self, file_path: str) -> bool:
        """Check if file matches include patterns."""
        if not self.include_patterns:
            return True
        
        for pattern in self.include_patterns:
            if self._matches_pattern(file_path, pattern):
                return True
        
        return False
    
    def _should_exclude(self, file_path: str) -> bool:
        """Check if file matches exclude patterns."""
        for pattern in self.exclude_patterns:
            if self._matches_pattern(file_path, pattern):
                return True
        
        return False
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches a glob pattern."""
        try:
            # Convert Unix-style path to OS-appropriate format for matching
            normalized_path = file_path.replace('\\', '/')
            normalized_pattern = pattern.replace('\\', '/')
            
            # Handle different pattern types
            if '**' in normalized_pattern:
                # Recursive pattern - use fnmatch with full path
                return fnmatch.fnmatch(normalized_path, normalized_pattern)
            elif '*' in normalized_pattern:
                # Simple glob pattern
                return fnmatch.fnmatch(normalized_path, normalized_pattern)
            else:
                # Exact match or substring
                return normalized_pattern in normalized_path
        
        except Exception as e:
            logger.warning(f"Error matching pattern '{pattern}' against '{file_path}': {e}")
            return False
    
    def _check_file_size(self, file_path: Path) -> bool:
        """Check if file size is within limits."""
        try:
            file_size = file_path.stat().st_size
            return file_size <= self.max_file_size_bytes
        except (OSError, PermissionError):
            # If we can't check size, assume it's okay
            return True


def read_repos_file(file_path: str) -> List[str]:
    """Read repository URLs from a text file."""
    repos = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Basic URL validation
                    if 'github.com' in line:
                        repos.append(line)
                    else:
                        logger.warning(f"Skipping invalid repository URL: {line}")
    
    except Exception as e:
        logger.error(f"Error reading repos file {file_path}: {e}")
        raise
    
    return repos


def ensure_directory(path: str) -> None:
    """Ensure directory exists, create if it doesn't."""
    Path(path).mkdir(parents=True, exist_ok=True)


def is_text_file(file_path: Path) -> bool:
    """Check if file is likely a text file."""
    try:
        # Check by extension first
        text_extensions = {
            '.txt', '.md', '.rst', '.py', '.js', '.ts', '.json', '.yaml', '.yml',
            '.xml', '.html', '.css', '.sql', '.sh', '.bat', '.ini', '.cfg', '.conf'
        }
        
        if file_path.suffix.lower() in text_extensions:
            return True
        
        # Try to read a small portion to detect binary content
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            
        # Check for null bytes (common in binary files)
        if b'\x00' in chunk:
            return False
        
        # Try to decode as UTF-8
        try:
            chunk.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False
    
    except (OSError, PermissionError):
        return False