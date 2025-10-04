"""
Main FastAPI application for AI Tools Database
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime

from database import get_db, init_db
from models import Provider, Tool, Category, ProviderSchemaModel, ToolExample
from schemas import (
    Provider, ProviderCreate, ProviderUpdate,
    Tool, ToolCreate, ToolUpdate, ToolSearchRequest, ToolSearchResponse,
    Category, CategoryCreate, CategoryUpdate,
    ProviderSchema, ProviderSchemaCreate, ProviderSchemaUpdate,
    ToolExample, ToolExampleCreate, ToolExampleUpdate,
    ConversionRequest, ConversionResponse, ValidationRequest, ValidationResultSchema,
    BatchValidationRequest, ApiResponse, HealthResponse, ProviderInfo,
    ProviderEnum
)
from converters import converter, StandardizedSchema
from validators import validator, batch_validator
from provider_schemas import ProviderType, EXAMPLE_TOOLS

# Initialize FastAPI app
app = FastAPI(
    title="AI Tools Database API",
    description="API for managing AI SDK tool and function definitions across multiple providers",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization failed (continuing without DB): {e}")

# Health endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        database_status="connected",
        supported_providers=converter.get_supported_providers()
    )

# Provider endpoints
@app.get("/api/providers", response_model=List[Provider])
async def get_providers(db: Session = Depends(get_db)):
    """Get all supported providers"""
    providers = db.query(Provider).all()
    return providers

@app.get("/api/providers/{provider_name}", response_model=Provider)
async def get_provider(provider_name: str, db: Session = Depends(get_db)):
    """Get provider by name"""
    provider = db.query(Provider).filter(Provider.name == provider_name).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

@app.get("/api/providers/{provider_name}/info", response_model=ProviderInfo)
async def get_provider_info(provider_name: str):
    """Get detailed information about a provider"""
    try:
        info = converter.get_provider_info(provider_name)
        return ProviderInfo(**info, is_supported=True)
    except ValueError:
        raise HTTPException(status_code=404, detail="Provider not supported")

# Category endpoints
@app.get("/api/categories", response_model=List[Category])
async def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    categories = db.query(Category).all()
    return categories

@app.post("/api/categories", response_model=Category)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category"""
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# Tool endpoints
@app.get("/api/tools", response_model=ToolSearchResponse)
async def search_tools(
    query: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    provider: Optional[ProviderEnum] = Query(None),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Search and filter tools"""
    query_obj = db.query(Tool)

    # Apply filters
    if query:
        query_obj = query_obj.filter(
            Tool.name.ilike(f"%{query}%") |
            Tool.description.ilike(f"%{query}%")
        )

    if category_id:
        query_obj = query_obj.filter(Tool.category_id == category_id)

    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        for tag in tag_list:
            query_obj = query_obj.filter(Tool.tags.contains([tag]))

    # Count total results
    total = query_obj.count()

    # Apply pagination
    tools = query_obj.offset(offset).limit(limit).all()

    return ToolSearchResponse(
        tools=tools,
        total=total,
        limit=limit,
        offset=offset
    )

@app.get("/api/tools/{tool_id}", response_model=Tool)
async def get_tool(tool_id: int, db: Session = Depends(get_db)):
    """Get tool by ID"""
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool

@app.post("/api/tools", response_model=Tool)
async def create_tool(tool: ToolCreate, db: Session = Depends(get_db)):
    """Create a new tool"""
    db_tool = Tool(**tool.dict())
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)
    return db_tool

@app.put("/api/tools/{tool_id}", response_model=Tool)
async def update_tool(tool_id: int, tool: ToolUpdate, db: Session = Depends(get_db)):
    """Update a tool"""
    db_tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not db_tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    for field, value in tool.dict(exclude_unset=True).items():
        setattr(db_tool, field, value)

    db.commit()
    db.refresh(db_tool)
    return db_tool

@app.delete("/api/tools/{tool_id}")
async def delete_tool(tool_id: int, db: Session = Depends(get_db)):
    """Delete a tool"""
    db_tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not db_tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    db.delete(db_tool)
    db.commit()
    return {"message": "Tool deleted successfully"}

# Schema conversion endpoints
@app.post("/api/convert", response_model=ConversionResponse)
async def convert_schema(request: ConversionRequest):
    """Convert schema from one provider format to another"""
    try:
        converted = converter.convert_schema(
            request.source_schema,
            request.source_provider.value,
            request.target_provider.value
        )
        return ConversionResponse(
            success=True,
            target_schema=converted,
            source_provider=request.source_provider.value,
            target_provider=request.target_provider.value
        )
    except Exception as e:
        return ConversionResponse(
            success=False,
            source_provider=request.source_provider.value,
            target_provider=request.target_provider.value,
            error=str(e)
        )

@app.get("/api/tools/{tool_id}/convert/{provider}")
async def convert_tool_schema(tool_id: int, provider: str, db: Session = Depends(get_db)):
    """Convert tool schema to specific provider format"""
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    try:
        converted = converter.convert_schema(
            tool.standardized_schema,
            "claude",  # Assuming standardized format is Claude-like
            provider
        )
        return {"success": True, "schema": converted}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Validation endpoints
@app.post("/api/validate", response_model=ValidationResultSchema)
async def validate_schema(request: ValidationRequest):
    """Validate a schema against provider rules"""
    result = validator.validate(
        request.schema,
        request.provider.value,
        request.strict
    )
    return ValidationResultSchema(**result.to_dict())

@app.post("/api/validate/batch")
async def validate_schemas_batch(request: BatchValidationRequest):
    """Validate multiple schemas"""
    if len(request.schemas) != len(request.providers):
        raise HTTPException(status_code=400, detail="Schemas and providers must have same length")

    schemas_providers = list(zip(request.schemas, [p.value for p in request.providers]))
    results = batch_validator.validate_batch(schemas_providers, request.strict)
    summary = batch_validator.get_summary(results)

    return {
        "results": [ValidationResultSchema(**r.to_dict()) for r in results],
        "summary": summary
    }

# Example endpoints
@app.get("/api/examples")
async def get_conversion_examples():
    """Get conversion examples"""
    return converter.get_conversion_examples()

@app.get("/api/examples/{tool_name}")
async def get_tool_example(tool_name: str, provider: ProviderEnum):
    """Get example tool schema for a provider"""
    if tool_name not in EXAMPLE_TOOLS:
        raise HTTPException(status_code=404, detail="Example tool not found")

    try:
        standard_schema = EXAMPLE_TOOLS[tool_name]
        converted = converter.convert_schema(
            standard_schema,
            "claude",  # Convert from Claude format
            provider.value
        )
        return {
            "tool_name": tool_name,
            "provider": provider.value,
            "schema": converted,
            "description": standard_schema["description"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Tool schema endpoints
@app.get("/api/tools/{tool_id}/schemas", response_model=List[ProviderSchema])
async def get_tool_schemas(tool_id: int, db: Session = Depends(get_db)):
    """Get all provider schemas for a tool"""
    schemas = db.query(ProviderSchemaModel).filter(
        ProviderSchemaModel.tool_id == tool_id
    ).all()
    return schemas

@app.post("/api/tools/{tool_id}/schemas", response_model=ProviderSchema)
async def create_tool_schema(
    tool_id: int,
    schema: ProviderSchemaCreate,
    db: Session = Depends(get_db)
):
    """Create a provider-specific schema for a tool"""
    # Verify tool exists
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    # Verify provider exists
    provider = db.query(Provider).filter(Provider.id == schema.provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    db_schema = ProviderSchemaModel(**schema.dict(), tool_id=tool_id)
    db.add(db_schema)
    db.commit()
    db.refresh(db_schema)
    return db_schema

# Tool example endpoints
@app.get("/api/tools/{tool_id}/examples", response_model=List[ToolExample])
async def get_tool_examples(tool_id: int, provider: Optional[str] = None, db: Session = Depends(get_db)):
    """Get examples for a tool"""
    query = db.query(ToolExample).filter(ToolExample.tool_id == tool_id)

    if provider:
        provider_obj = db.query(Provider).filter(Provider.name == provider).first()
        if provider_obj:
            query = query.filter(ToolExample.provider_id == provider_obj.id)

    examples = query.all()
    return examples

@app.post("/api/tools/{tool_id}/examples", response_model=ToolExample)
async def create_tool_example(
    tool_id: int,
    example: ToolExampleCreate,
    db: Session = Depends(get_db)
):
    """Create an example for a tool"""
    # Verify tool exists
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    db_example = ToolExample(**example.dict(), tool_id=tool_id)
    db.add(db_example)
    db.commit()
    db.refresh(db_example)
    return db_example

# Populate examples endpoint
@app.post("/api/populate-examples")
async def populate_examples(db: Session = Depends(get_db)):
    """Populate database with example tools"""
    try:
        # Get providers
        providers = {p.name: p for p in db.query(Provider).all()}

        # Get utilities category
        category = db.query(Category).filter(Category.name == "utilities").first()

        for tool_name, tool_data in EXAMPLE_TOOLS.items():
            # Create tool if it doesn't exist
            existing_tool = db.query(Tool).filter(Tool.name == tool_name).first()
            if not existing_tool:
                tool = Tool(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    category_id=category.id if category else None,
                    standardized_schema=tool_data,
                    tags=tool_data.get("tags", [])
                )
                db.add(tool)
                db.commit()
                db.refresh(tool)

                # Create provider schemas
                for provider_name in ["openai", "claude", "gemini", "mistral"]:
                    if provider_name in providers:
                        try:
                            converted_schema = converter.convert_schema(
                                tool_data,
                                "claude",  # Source format
                                provider_name
                            )

                            provider_schema = ProviderSchemaModel(
                                tool_id=tool.id,
                                provider_id=providers[provider_name].id,
                                schema_format=converted_schema,
                                is_supported=True
                            )
                            db.add(provider_schema)
                        except Exception as e:
                            print(f"Failed to convert {tool_name} for {provider_name}: {e}")

                db.commit()

        return {"message": "Examples populated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)