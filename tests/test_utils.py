"""Tests for utility functions."""

import pytest
from pathlib import Path

from aipm_github_harvester.utils.file_utils import FileScanner, read_repos_file


class TestFileScanner:
    """Tests for file scanner utility."""
    
    def test_file_scanner_creation(self):
        """Test FileScanner initialization."""
        scanner = FileScanner(
            include_patterns=["*.md", "*.py"],
            exclude_patterns=[".git/**", "*.pyc"],
            max_file_size_mb=5
        )
        
        assert "*.md" in scanner.include_patterns
        assert ".git/**" in scanner.exclude_patterns
        assert scanner.max_file_size_bytes == 5 * 1024 * 1024
    
    def test_should_include(self):
        """Test include pattern matching."""
        scanner = FileScanner(
            include_patterns=["README*", "docs/**", "*.py"],
            exclude_patterns=[],
            max_file_size_mb=10
        )
        
        assert scanner._should_include("README.md")
        assert scanner._should_include("docs/guide.md")
        assert scanner._should_include("main.py")
        assert not scanner._should_include("other.txt")
    
    def test_should_exclude(self):
        """Test exclude pattern matching."""
        scanner = FileScanner(
            include_patterns=["**"],
            exclude_patterns=[".git/**", "*.pyc", "node_modules/**"],
            max_file_size_mb=10
        )
        
        assert scanner._should_exclude(".git/config")
        assert scanner._should_exclude("test.pyc")
        assert scanner._should_exclude("node_modules/package.json")
        assert not scanner._should_exclude("src/main.py")
    
    def test_matches_pattern(self):
        """Test pattern matching logic."""
        scanner = FileScanner([], [], 10)
        
        # Test exact matches
        assert scanner._matches_pattern("README.md", "README.md")
        
        # Test glob patterns
        assert scanner._matches_pattern("README.md", "README*")
        assert scanner._matches_pattern("docs/guide.md", "docs/*.md")
        
        # Test recursive patterns
        assert scanner._matches_pattern("src/utils/helper.py", "**/*.py")


def test_read_repos_file(temp_repos_file):
    """Test reading repository URLs from file."""
    repos = read_repos_file(temp_repos_file)
    
    assert len(repos) == 3
    assert "https://github.com/test/repo1" in repos
    assert "https://github.com/example/repo2" in repos
    assert "https://github.com/demo/repo3" in repos
    # Comment lines should be ignored


def test_read_repos_file_nonexistent():
    """Test reading non-existent repos file."""
    with pytest.raises(Exception):
        read_repos_file("nonexistent.txt")