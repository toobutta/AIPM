"""
Pydantic schemas for API request/response models
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class ProviderEnum(str, Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    MISTRAL = "mistral"
    COHERE = "cohere"

class ProviderBase(BaseModel):
    name: str = Field(..., description="Provider name")
    display_name: str = Field(..., description="Display name")
    api_version: Optional[str] = Field(None, description="API version")
    description: Optional[str] = Field(None, description="Provider description")
    base_url: Optional[str] = Field(None, description="Base URL")
    documentation_url: Optional[str] = Field(None, description="Documentation URL")

class ProviderCreate(ProviderBase):
    pass

class ProviderUpdate(BaseModel):
    display_name: Optional[str] = None
    api_version: Optional[str] = None
    description: Optional[str] = None
    base_url: Optional[str] = None
    documentation_url: Optional[str] = None

class Provider(ProviderBase):
    id: int
    schema_format: str = Field(default="json_schema")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    parent_id: Optional[int] = Field(None, description="Parent category ID")

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None

class Category(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ToolBase(BaseModel):
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    category_id: Optional[int] = Field(None, description="Category ID")
    standardized_schema: Dict[str, Any] = Field(..., description="Standardized schema")
    tags: Optional[List[str]] = Field(default=[], description="Tool tags")
    is_public: bool = Field(default=True, description="Is public")

class ToolCreate(ToolBase):
    pass

class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    standardized_schema: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None

class Tool(ToolBase):
    id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[Category] = None

    class Config:
        from_attributes = True

class ProviderSchemaBase(BaseModel):
    tool_id: int = Field(..., description="Tool ID")
    provider_id: int = Field(..., description="Provider ID")
    schema_format: Dict[str, Any] = Field(..., description="Provider-specific schema")
    field_mappings: Optional[Dict[str, Any]] = Field(None, description="Field mappings")
    is_supported: bool = Field(default=True, description="Is supported")
    version: Optional[str] = Field(None, description="Schema version")

class ProviderSchemaCreate(ProviderSchemaBase):
    pass

class ProviderSchemaUpdate(BaseModel):
    schema_format: Optional[Dict[str, Any]] = None
    field_mappings: Optional[Dict[str, Any]] = None
    is_supported: Optional[bool] = None
    version: Optional[str] = None

class ProviderSchema(ProviderSchemaBase):
    id: int
    created_at: datetime
    updated_at: datetime
    tool: Optional[Tool] = None
    provider: Optional[Provider] = None

    class Config:
        from_attributes = True

class ToolExampleBase(BaseModel):
    tool_id: int = Field(..., description="Tool ID")
    provider_id: int = Field(..., description="Provider ID")
    example_name: str = Field(..., description="Example name")
    description: Optional[str] = Field(None, description="Example description")
    input_data: Optional[Dict[str, Any]] = Field(None, description="Input data")
    expected_output: Optional[Dict[str, Any]] = Field(None, description="Expected output")
    usage_context: Optional[str] = Field(None, description="Usage context")

class ToolExampleCreate(ToolExampleBase):
    pass

class ToolExampleUpdate(BaseModel):
    example_name: Optional[str] = None
    description: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    expected_output: Optional[Dict[str, Any]] = None
    usage_context: Optional[str] = None

class ToolExample(ToolExampleBase):
    id: int
    created_at: datetime
    tool: Optional[Tool] = None
    provider: Optional[Provider] = None

    class Config:
        from_attributes = True

class ValidationErrorSchema(BaseModel):
    field: str
    message: str
    type: str = Field(default="error")

class ValidationResultSchema(BaseModel):
    is_valid: bool
    errors: List[ValidationErrorSchema] = Field(default=[])
    warnings: List[ValidationErrorSchema] = Field(default=[])
    error_count: int
    warning_count: int

class ConversionRequest(BaseModel):
    source_schema: Dict[str, Any] = Field(..., description="Source schema")
    source_provider: ProviderEnum = Field(..., description="Source provider")
    target_provider: ProviderEnum = Field(..., description="Target provider")

class ConversionResponse(BaseModel):
    success: bool
    target_schema: Optional[Dict[str, Any]] = None
    source_provider: str
    target_provider: str
    error: Optional[str] = None

class ValidationRequest(BaseModel):
    schema: Dict[str, Any] = Field(..., description="Schema to validate")
    provider: ProviderEnum = Field(..., description="Provider")
    strict: bool = Field(default=False, description="Strict validation")

class BatchValidationRequest(BaseModel):
    schemas: List[Dict[str, Any]] = Field(..., description="List of schemas to validate")
    providers: List[ProviderEnum] = Field(..., description="List of providers")
    strict: bool = Field(default=False, description="Strict validation")

class ToolSearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="Search query")
    category_id: Optional[int] = Field(None, description="Category ID")
    provider: Optional[ProviderEnum] = Field(None, description="Provider filter")
    tags: Optional[List[str]] = Field(None, description="Tag filter")
    limit: int = Field(default=20, ge=1, le=100, description="Result limit")
    offset: int = Field(default=0, ge=0, description="Result offset")

class ToolSearchResponse(BaseModel):
    tools: List[Tool]
    total: int
    limit: int
    offset: int

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = Field(default="1.0.0")
    database_status: str
    supported_providers: List[str]

class ProviderInfo(BaseModel):
    name: str
    display_name: str
    validation_rules: Dict[str, Any]
    field_mappings: Dict[str, Any]
    is_supported: bool

class ConversionExample(BaseModel):
    source_schema: Dict[str, Any]
    target_schema: Dict[str, Any]
    source_provider: str
    target_provider: str
    description: str