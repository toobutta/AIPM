"""Export utilities for different output formats."""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any
import logging
from datetime import datetime

from ..core.models import HarvestResult, AIToolMetadata
from ..utils.file_utils import ensure_directory

logger = logging.getLogger(__name__)


class JSONLExporter:
    """Exporter for JSONL (JSON Lines) format."""
    
    def export_results(self, results: List[HarvestResult], output_dir: str) -> None:
        """Export harvest results to JSONL files."""
        ensure_directory(output_dir)
        
        # Main metadata file
        metadata_file = Path(output_dir) / "harvested_metadata.jsonl"
        
        # Repository-specific files
        repo_dir = Path(output_dir) / "repositories"
        ensure_directory(str(repo_dir))
        
        # Function-specific files
        func_dir = Path(output_dir) / "functions"
        ensure_directory(str(func_dir))
        
        all_tools = []
        
        with open(metadata_file, 'w', encoding='utf-8') as main_file:
            for result in results:
                # Write to repository-specific file
                repo_name = self._safe_filename(f"{result.repository.owner}_{result.repository.name}")
                repo_file = repo_dir / f"{repo_name}.jsonl"
                
                with open(repo_file, 'w', encoding='utf-8') as rf:
                    # Write repository info
                    repo_data = {
                        "type": "repository",
                        "data": result.repository.model_dump(),
                        "harvest_info": {
                            "total_files_scanned": result.total_files_scanned,
                            "total_tools_extracted": result.total_tools_extracted,
                            "processing_time_seconds": result.processing_time_seconds,
                            "errors": result.errors,
                            "warnings": result.warnings,
                            "harvest_timestamp": result.harvest_timestamp.isoformat()
                        }
                    }
                    rf.write(json.dumps(repo_data, default=str) + '\n')
                    
                    # Write tools for this repository
                    for tool in result.tools_found:
                        tool_data = {
                            "type": "tool",
                            "data": tool.model_dump()
                        }
                        rf.write(json.dumps(tool_data, default=str) + '\n')
                        main_file.write(json.dumps(tool.model_dump(), default=str) + '\n')
                        all_tools.append(tool)
        
        # Export function-specific files
        self._export_function_files(all_tools, str(func_dir))
        
        logger.info(f"Exported {len(all_tools)} tools to JSONL format in {output_dir}")
    
    def _export_function_files(self, tools: List[AIToolMetadata], func_dir: str) -> None:
        """Export tools grouped by provider to function-specific files."""
        provider_tools = {}
        
        for tool in tools:
            provider = tool.provider or "unknown"
            if provider not in provider_tools:
                provider_tools[provider] = []
            provider_tools[provider].append(tool)
        
        for provider, provider_tool_list in provider_tools.items():
            safe_provider = self._safe_filename(provider)
            func_file = Path(func_dir) / f"{safe_provider}_functions.jsonl"
            
            with open(func_file, 'w', encoding='utf-8') as f:
                for tool in provider_tool_list:
                    for func in tool.functions:
                        func_data = {
                            "tool_name": tool.name,
                            "provider": provider,
                            "repository_url": str(tool.repository_url),
                            "function": func.model_dump(),
                            "extracted_at": tool.extracted_at.isoformat()
                        }
                        f.write(json.dumps(func_data, default=str) + '\n')
    
    def _safe_filename(self, name: str) -> str:
        """Convert name to safe filename."""
        # Replace unsafe characters
        safe = name.lower()
        safe = ''.join(c if c.isalnum() or c in '-_' else '_' for c in safe)
        safe = safe.replace('__', '_').strip('_')
        return safe or 'unnamed'


class CSVExporter:
    """Exporter for CSV format."""
    
    def export_results(self, results: List[HarvestResult], output_dir: str) -> None:
        """Export harvest results to CSV files."""
        ensure_directory(output_dir)
        
        # Main metadata CSV
        metadata_file = Path(output_dir) / "harvested_metadata.csv"
        
        # Functions CSV
        functions_file = Path(output_dir) / "extracted_functions.csv" 
        
        # Repository CSV
        repositories_file = Path(output_dir) / "processed_repositories.csv"
        
        all_tools = []
        all_functions = []
        all_repos = []
        
        # Collect data from all results
        for result in results:
            all_repos.append(result.repository)
            all_tools.extend(result.tools_found)
            
            for tool in result.tools_found:
                for func in tool.functions:
                    func_record = {
                        'tool_name': tool.name,
                        'provider': tool.provider or '',
                        'repository_url': str(tool.repository_url) if tool.repository_url else '',
                        'function_name': func.name,
                        'function_description': func.description or '',
                        'parameter_count': len(func.parameters),
                        'tags': ', '.join(func.tags),
                        'extracted_at': tool.extracted_at.isoformat()
                    }
                    all_functions.append(func_record)
        
        # Export tools CSV
        if all_tools:
            self._export_tools_csv(all_tools, metadata_file)
        
        # Export functions CSV
        if all_functions:
            self._export_functions_csv(all_functions, functions_file)
        
        # Export repositories CSV
        if all_repos:
            self._export_repositories_csv(all_repos, repositories_file)
        
        logger.info(f"Exported {len(all_tools)} tools to CSV format in {output_dir}")
    
    def _export_tools_csv(self, tools: List[AIToolMetadata], file_path: Path) -> None:
        """Export tools to CSV."""
        fieldnames = [
            'name', 'description', 'provider', 'version', 'repository_url',
            'function_count', 'invocation_paradigms', 'protocols', 'model',
            'tags', 'categories', 'confidence_score', 'discovered_from',
            'extraction_method', 'extracted_at'
        ]
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for tool in tools:
                row = {
                    'name': tool.name,
                    'description': tool.description or '',
                    'provider': tool.provider or '',
                    'version': tool.version or '',
                    'repository_url': str(tool.repository_url) if tool.repository_url else '',
                    'function_count': len(tool.functions),
                    'invocation_paradigms': ', '.join(tool.invocation_paradigm),
                    'protocols': ', '.join(tool.protocol),
                    'model': tool.model or '',
                    'tags': ', '.join(tool.tags),
                    'categories': ', '.join(tool.categories),
                    'confidence_score': tool.confidence_score,
                    'discovered_from': ', '.join(tool.discovered_from),
                    'extraction_method': ', '.join(tool.extraction_method),
                    'extracted_at': tool.extracted_at.isoformat()
                }
                writer.writerow(row)
    
    def _export_functions_csv(self, functions: List[Dict[str, Any]], file_path: Path) -> None:
        """Export functions to CSV."""
        if not functions:
            return
        
        fieldnames = list(functions[0].keys())
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(functions)
    
    def _export_repositories_csv(self, repositories, file_path: Path) -> None:
        """Export repositories to CSV."""
        fieldnames = [
            'name', 'full_name', 'owner', 'description', 'url',
            'primary_language', 'stars', 'forks', 'size', 'topics',
            'license', 'created_at', 'updated_at', 'archived'
        ]
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for repo in repositories:
                row = {
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'owner': repo.owner,
                    'description': repo.description or '',
                    'url': str(repo.url),
                    'primary_language': repo.primary_language or '',
                    'stars': repo.stars,
                    'forks': repo.forks,
                    'size': repo.size,
                    'topics': ', '.join(repo.topics),
                    'license': repo.license or '',
                    'created_at': repo.created_at.isoformat() if repo.created_at else '',
                    'updated_at': repo.updated_at.isoformat() if repo.updated_at else '',
                    'archived': repo.archived
                }
                writer.writerow(row)


class ExporterFactory:
    """Factory for creating exporters based on format."""
    
    @staticmethod
    def get_exporter(format_name: str):
        """Get exporter for the specified format."""
        exporters = {
            'jsonl': JSONLExporter,
            'csv': CSVExporter,
        }
        
        exporter_class = exporters.get(format_name.lower())
        if exporter_class:
            return exporter_class()
        else:
            raise ValueError(f"Unsupported export format: {format_name}")
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """Get list of supported export formats."""
        return ['jsonl', 'csv']