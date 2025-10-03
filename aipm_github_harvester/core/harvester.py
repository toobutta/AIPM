"""Core harvester implementation."""

import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Iterator, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from urllib.parse import urlparse

import git
from rich.console import Console
from rich.progress import Progress, TaskID

from .models import (
    HarvestConfig, 
    HarvestResult, 
    RepositoryMetadata, 
    AIToolMetadata,
    FileParseResult
)
from ..parsers.factory import ParserFactory
from ..utils.github_client import GitHubClient
from ..utils.file_utils import FileScanner


logger = logging.getLogger(__name__)


class GitHubHarvester:
    """Main harvester class for extracting AI tool metadata from GitHub repositories."""
    
    def __init__(self, config: Optional[HarvestConfig] = None) -> None:
        """Initialize the harvester with configuration."""
        self.config = config or HarvestConfig()
        self.console = Console()
        self.parser_factory = ParserFactory()
        self.github_client = GitHubClient(token=self.config.github_token)
        self.file_scanner = FileScanner(
            include_patterns=self.config.include_patterns,
            exclude_patterns=self.config.exclude_patterns,
            max_file_size_mb=self.config.max_file_size_mb
        )
    
    def harvest_repositories(self, repo_urls: List[str]) -> Iterator[HarvestResult]:
        """Harvest metadata from multiple repositories."""
        total_repos = len(repo_urls)
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Harvesting repositories...", total=total_repos)
            
            if self.config.parallel_processing:
                yield from self._harvest_parallel(repo_urls, progress, task)
            else:
                yield from self._harvest_sequential(repo_urls, progress, task)
    
    def harvest_repository(self, repo_url: str) -> HarvestResult:
        """Harvest metadata from a single repository."""
        logger.info(f"Starting harvest of repository: {repo_url}")
        
        result = HarvestResult(
            repository=RepositoryMetadata(
                url=repo_url,
                name="",
                full_name="",
                owner=""
            )
        )
        
        temp_dir = None
        try:
            # Get repository metadata from GitHub API if available
            if self.config.use_github_api:
                try:
                    repo_info = self.github_client.get_repository_info(repo_url)
                    result.repository = RepositoryMetadata(**repo_info)
                except Exception as e:
                    logger.warning(f"Could not fetch repo info from API: {e}")
                    result.warnings.append(f"GitHub API unavailable: {e}")
            
            # Clone repository
            temp_dir = self._clone_repository(repo_url)
            if not temp_dir:
                result.errors.append("Failed to clone repository")
                return result
            
            # Scan for relevant files
            relevant_files = self.file_scanner.scan_directory(temp_dir)
            result.total_files_scanned = len(relevant_files)
            
            logger.info(f"Found {len(relevant_files)} relevant files to process")
            
            # Process files and extract metadata
            all_tools = []
            for file_path in relevant_files:
                try:
                    parse_result = self._parse_file(file_path, temp_dir)
                    result.files_processed.append(parse_result)
                    
                    if parse_result.success:
                        all_tools.extend(parse_result.metadata)
                        
                except Exception as e:
                    error_msg = f"Error processing file {file_path}: {e}"
                    logger.error(error_msg)
                    result.errors.append(error_msg)
                    
                    # Create error result for tracking
                    error_result = FileParseResult(
                        file_path=str(file_path),
                        file_type="unknown",
                        parser_used="none",
                        success=False,
                        errors=[str(e)]
                    )
                    result.files_processed.append(error_result)
            
            # Deduplicate and enhance metadata
            result.tools_found = self._deduplicate_tools(all_tools)
            result.total_tools_extracted = len(result.tools_found)
            
            # Enhance tools with repository context
            for tool in result.tools_found:
                if not tool.provider and result.repository.owner:
                    tool.provider = result.repository.owner
                if not tool.repository_url:
                    tool.repository_url = repo_url
                if result.repository.license and not tool.license:
                    tool.license = result.repository.license
            
            logger.info(f"Successfully extracted {result.total_tools_extracted} tools from {repo_url}")
            
        except Exception as e:
            error_msg = f"Failed to harvest repository {repo_url}: {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)
            
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        return result
    
    def _harvest_parallel(
        self, 
        repo_urls: List[str], 
        progress: Progress, 
        task: TaskID
    ) -> Iterator[HarvestResult]:
        """Harvest repositories in parallel."""
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_url = {
                executor.submit(self.harvest_repository, url): url 
                for url in repo_urls
            }
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    progress.update(task, advance=1)
                    yield result
                except Exception as e:
                    logger.error(f"Error harvesting {url}: {e}")
                    error_result = HarvestResult(
                        repository=RepositoryMetadata(
                            url=url,
                            name="",
                            full_name="",
                            owner=""
                        ),
                        errors=[str(e)]
                    )
                    progress.update(task, advance=1)
                    yield error_result
    
    def _harvest_sequential(
        self, 
        repo_urls: List[str], 
        progress: Progress, 
        task: TaskID
    ) -> Iterator[HarvestResult]:
        """Harvest repositories sequentially."""
        for url in repo_urls:
            try:
                result = self.harvest_repository(url)
                progress.update(task, advance=1)
                yield result
            except Exception as e:
                logger.error(f"Error harvesting {url}: {e}")
                error_result = HarvestResult(
                    repository=RepositoryMetadata(
                        url=url,
                        name="",
                        full_name="",
                        owner=""
                    ),
                    errors=[str(e)]
                )
                progress.update(task, advance=1)
                yield error_result
    
    def _clone_repository(self, repo_url: str) -> Optional[str]:
        """Clone repository to temporary directory."""
        try:
            temp_dir = tempfile.mkdtemp(prefix="aipm_harvest_")
            logger.debug(f"Cloning {repo_url} to {temp_dir}")
            
            git.Repo.clone_from(
                repo_url, 
                temp_dir,
                depth=self.config.clone_depth,
                single_branch=True
            )
            
            return temp_dir
            
        except Exception as e:
            logger.error(f"Failed to clone repository {repo_url}: {e}")
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            return None
    
    def _parse_file(self, file_path: Path, repo_root: str) -> FileParseResult:
        """Parse a single file and extract metadata."""
        relative_path = file_path.relative_to(repo_root)
        
        # Determine file type and get appropriate parser
        file_type = self._determine_file_type(file_path)
        parser = self.parser_factory.get_parser(file_type)
        
        if not parser:
            return FileParseResult(
                file_path=str(relative_path),
                file_type=file_type,
                parser_used="none",
                success=False,
                errors=[f"No parser available for file type: {file_type}"]
            )
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse content
            metadata_list = parser.parse(content, str(relative_path))
            
            return FileParseResult(
                file_path=str(relative_path),
                file_type=file_type,
                parser_used=parser.__class__.__name__,
                success=True,
                metadata=metadata_list,
                raw_content=content if len(content) < 50000 else content[:50000] + "...[truncated]"
            )
            
        except Exception as e:
            return FileParseResult(
                file_path=str(relative_path),
                file_type=file_type,
                parser_used=parser.__class__.__name__ if parser else "none",
                success=False,
                errors=[str(e)]
            )
    
    def _determine_file_type(self, file_path: Path) -> str:
        """Determine file type based on path and extension."""
        name = file_path.name.lower()
        suffix = file_path.suffix.lower()
        
        # README files
        if name.startswith('readme'):
            return 'readme'
        
        # OpenAPI specs
        if 'openapi' in str(file_path).lower() or 'swagger' in str(file_path).lower():
            if suffix in ['.json', '.yaml', '.yml']:
                return 'openapi'
        
        # MCP configs
        if 'mcp' in str(file_path).lower():
            return 'mcp'
        
        # Tools directory
        if 'tools' in str(file_path).parts:
            return 'tools'
        
        # Documentation
        if 'docs' in str(file_path).parts:
            return 'documentation'
        
        # File extensions
        if suffix in ['.json', '.yaml', '.yml']:
            return 'config'
        elif suffix in ['.py']:
            return 'python'
        elif suffix in ['.js', '.ts']:
            return 'javascript'
        elif suffix in ['.md']:
            return 'markdown'
        
        return 'unknown'
    
    def _deduplicate_tools(self, tools: List[AIToolMetadata]) -> List[AIToolMetadata]:
        """Deduplicate extracted tools based on name and function signatures."""
        seen = set()
        unique_tools = []
        
        for tool in tools:
            # Create a signature for deduplication
            signature = (
                tool.name,
                len(tool.functions),
                tuple(f.name for f in tool.functions) if tool.functions else ()
            )
            
            if signature not in seen:
                seen.add(signature)
                unique_tools.append(tool)
            else:
                # Merge additional information from duplicates
                existing = next(t for t in unique_tools if (
                    t.name, 
                    len(t.functions),
                    tuple(f.name for f in t.functions) if t.functions else ()
                ) == signature)
                
                # Merge discovered_from and extraction_method
                existing.discovered_from.extend(tool.discovered_from)
                existing.extraction_method.extend(tool.extraction_method)
                existing.discovered_from = list(set(existing.discovered_from))
                existing.extraction_method = list(set(existing.extraction_method))
        
        return unique_tools