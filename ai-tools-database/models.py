"""
Database models for AI Tools Database
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Provider(Base):
    __tablename__ = 'providers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    api_version = Column(String(20))
    description = Column(Text)
    base_url = Column(String(255))
    documentation_url = Column(String(255))
    schema_format = Column(String(20), default='json_schema')
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    provider_schemas = relationship("ProviderSchema", back_populates="provider")
    tool_examples = relationship("ToolExample", back_populates="provider")
    field_mappings = relationship("FieldMapping", foreign_keys="FieldMapping.from_provider_id", back_populates="from_provider")
    reverse_mappings = relationship("FieldMapping", foreign_keys="FieldMapping.to_provider_id", back_populates="to_provider")
    validation_rules = relationship("ValidationRule", back_populates="provider")
    api_usage = relationship("APIUsage", back_populates="provider")

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey('categories.id'))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    parent = relationship("Category", remote_side=[id])
    children = relationship("Category")
    tools = relationship("Tool", back_populates="category")

class Tool(Base):
    __tablename__ = 'tools'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    standardized_schema = Column(JSONB, nullable=False)
    tags = Column(JSONB)  # Array of strings stored as JSONB
    is_public = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("Category", back_populates="tools")
    provider_schemas = relationship("ProviderSchemaModel", back_populates="tool")
    tool_examples = relationship("ToolExample", back_populates="tool")
    api_usage = relationship("APIUsage", back_populates="tool")

class ProviderSchemaModel(Base):
    __tablename__ = 'provider_schemas'

    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey('tools.id', ondelete='CASCADE'), nullable=False)
    provider_id = Column(Integer, ForeignKey('providers.id', ondelete='CASCADE'), nullable=False)
    schema_format = Column(JSONB, nullable=False)
    field_mappings = Column(JSONB)
    is_supported = Column(Boolean, default=True)
    version = Column(String(20))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tool = relationship("Tool", back_populates="provider_schemas")
    provider = relationship("Provider", back_populates="provider_schemas")

class ToolExample(Base):
    __tablename__ = 'tool_examples'

    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey('tools.id', ondelete='CASCADE'), nullable=False)
    provider_id = Column(Integer, ForeignKey('providers.id', ondelete='CASCADE'), nullable=False)
    example_name = Column(String(100), nullable=False)
    description = Column(Text)
    input_data = Column(JSONB)
    expected_output = Column(JSONB)
    usage_context = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    tool = relationship("Tool", back_populates="tool_examples")
    provider = relationship("Provider", back_populates="tool_examples")

class FieldMapping(Base):
    __tablename__ = 'field_mappings'

    id = Column(Integer, primary_key=True, index=True)
    from_provider_id = Column(Integer, ForeignKey('providers.id'), nullable=False)
    to_provider_id = Column(Integer, ForeignKey('providers.id'), nullable=False)
    field_mapping = Column(JSONB, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    from_provider = relationship("Provider", foreign_keys=[from_provider_id], back_populates="field_mappings")
    to_provider = relationship("Provider", foreign_keys=[to_provider_id], back_populates="reverse_mappings")

class ValidationRule(Base):
    __tablename__ = 'validation_rules'

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey('providers.id'), nullable=False)
    rule_name = Column(String(100), nullable=False)
    rule_type = Column(String(50), nullable=False)
    rule_definition = Column(JSONB, nullable=False)
    error_message = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    provider = relationship("Provider", back_populates="validation_rules")

class APIUsage(Base):
    __tablename__ = 'api_usage'

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey('providers.id'), nullable=False)
    tool_id = Column(Integer, ForeignKey('tools.id'))
    request_type = Column(String(50), nullable=False)
    request_data = Column(JSONB)
    response_status = Column(Integer)
    response_time_ms = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    provider = relationship("Provider", back_populates="api_usage")
    tool = relationship("Tool", back_populates="api_usage")