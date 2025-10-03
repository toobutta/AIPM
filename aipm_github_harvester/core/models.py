"""Core data models for AIPM GitHub Harvester."""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class InvocationParadigm(str, Enum):
    """How AI tools are invoked."""
    API = "api"
    CLI = "cli"
    SDK = "sdk"
    WEBHOOK = "webhook"
    FUNCTION_CALL = "function_call"
    PLUGIN = "plugin"
    LIBRARY = "library"
    SERVICE = "service"


class Protocol(str, Enum):
    """Communication protocols."""
    HTTP = "http"
    HTTPS = "https"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    REST = "rest"
    GRAPHQL = "graphql"
    MCP = "mcp"
    OPENAPI = "openapi"


class SchemaType(str, Enum):
    """Schema definition types."""
    JSON_SCHEMA = "json_schema"
    OPENAPI = "openapi"
    PYDANTIC = "pydantic"
    TYPESCRIPT = "typescript"
    PYTHON = "python"
    YAML = "yaml"


class FunctionParameter(BaseModel):
    """Function parameter definition."""
    name: str
    type: str
    description: Optional[str] = None
    required: bool = False
    default: Optional[Any] = None
    param_schema: Optional[Dict[str, Any]] = Field(None, alias="schema")


class FunctionDefinition(BaseModel):
    """AI tool function definition."""
    name: str
    description: Optional[str] = None
    parameters: List[FunctionParameter] = Field(default_factory=list)
    return_type: Optional[str] = None
    return_schema: Optional[Dict[str, Any]] = None
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class AIToolMetadata(BaseModel):
    """Complete AI tool metadata extracted from repositories."""
    # Core identification
    name: str
    description: Optional[str] = None
    repository_url: Optional[HttpUrl] = None
    provider: Optional[str] = None
    version: Optional[str] = None
    
    # AIPM core fields
    functions: List[FunctionDefinition] = Field(default_factory=list)
    invocation_paradigm: List[InvocationParadigm] = Field(default_factory=list)
    protocol: List[Protocol] = Field(default_factory=list)
    
    # Schema information
    args_schema: Optional[Dict[str, Any]] = None
    result_schema: Optional[Dict[str, Any]] = None
    schema_type: Optional[SchemaType] = None
    
    # Model and compatibility
    model: Optional[str] = None
    model_requirements: List[str] = Field(default_factory=list)
    compatible_models: List[str] = Field(default_factory=list)
    
    # Discovery metadata
    discovered_from: List[str] = Field(default_factory=list)  # File paths where found
    extraction_method: List[str] = Field(default_factory=list)  # How it was extracted
    confidence_score: float = 0.0
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    license: Optional[str] = None
    documentation_url: Optional[HttpUrl] = None
    api_endpoint: Optional[HttpUrl] = None
    
    # Timestamps
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    repository_updated_at: Optional[datetime] = None


class RepositoryMetadata(BaseModel):
    """Metadata about the source repository."""
    url: HttpUrl
    name: str
    full_name: str
    owner: str
    description: Optional[str] = None
    primary_language: Optional[str] = None
    languages: Dict[str, int] = Field(default_factory=dict)
    topics: List[str] = Field(default_factory=list)
    stars: int = 0
    forks: int = 0
    size: int = 0
    default_branch: str = "main"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    pushed_at: Optional[datetime] = None
    license: Optional[str] = None
    has_wiki: bool = False
    has_pages: bool = False
    archived: bool = False
    disabled: bool = False


class FileParseResult(BaseModel):
    """Result of parsing a single file."""
    file_path: str
    file_type: str
    parser_used: str
    success: bool
    metadata: List[AIToolMetadata] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    raw_content: Optional[str] = None
    extracted_sections: Dict[str, Any] = Field(default_factory=dict)


class HarvestResult(BaseModel):
    """Complete harvest result for a repository."""
    repository: RepositoryMetadata
    tools_found: List[AIToolMetadata] = Field(default_factory=list)
    files_processed: List[FileParseResult] = Field(default_factory=list)
    total_files_scanned: int = 0
    total_tools_extracted: int = 0
    processing_time_seconds: float = 0.0
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    harvest_timestamp: datetime = Field(default_factory=datetime.utcnow)


class HarvestConfig(BaseModel):
    """Configuration for the harvesting process."""
    # Repository settings
    clone_depth: int = 1
    max_file_size_mb: int = 10
    timeout_seconds: int = 300
    
    # Parsing settings
    include_patterns: List[str] = Field(default_factory=lambda: [
        "docs/**",
        "README*",
        "examples/**",
        "openapi/*.json",
        "openapi/*.yaml",
        "openapi/*.yml",
        "mcp/**",
        "tools/**",
    ])
    exclude_patterns: List[str] = Field(default_factory=lambda: [
        "node_modules/**",
        ".git/**",
        "**/__pycache__/**",
        "**/.*",
        "**/*.pyc",
        "**/build/**",
        "**/dist/**",
    ])
    
    # Output settings
    output_formats: List[str] = Field(default_factory=lambda: ["jsonl", "csv"])
    base_output_dir: str = "data/registry"
    create_separate_files: bool = True
    
    # GitHub settings
    github_token: Optional[str] = None
    use_github_api: bool = True
    api_rate_limit_delay: float = 1.0
    
    # Processing settings
    parallel_processing: bool = True
    max_workers: int = 4
    enable_caching: bool = True
    cache_dir: str = ".cache"