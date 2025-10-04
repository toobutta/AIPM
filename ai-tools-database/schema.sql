-- AI SDK Tool & Function Definition Database Schema
-- PostgreSQL with JSONB support

-- AI Providers table
CREATE TABLE providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    api_version VARCHAR(20),
    description TEXT,
    base_url VARCHAR(255),
    documentation_url VARCHAR(255),
    schema_format VARCHAR(20) DEFAULT 'json_schema',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tool Categories
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    parent_id INTEGER REFERENCES categories(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Core Tools table (standardized format)
CREATE TABLE tools (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    standardized_schema JSONB NOT NULL,
    tags TEXT[],
    is_public BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(name, category_id)
);

-- Provider-specific tool schemas
CREATE TABLE provider_schemas (
    id SERIAL PRIMARY KEY,
    tool_id INTEGER NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
    provider_id INTEGER NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    schema_format JSONB NOT NULL,
    field_mappings JSONB,
    is_supported BOOLEAN DEFAULT true,
    version VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tool_id, provider_id)
);

-- Tool examples for each provider
CREATE TABLE tool_examples (
    id SERIAL PRIMARY KEY,
    tool_id INTEGER NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
    provider_id INTEGER NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    example_name VARCHAR(100) NOT NULL,
    description TEXT,
    input_data JSONB,
    expected_output JSONB,
    usage_context TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tool_id, provider_id, example_name)
);

-- Field mappings between provider formats
CREATE TABLE field_mappings (
    id SERIAL PRIMARY KEY,
    from_provider_id INTEGER NOT NULL REFERENCES providers(id),
    to_provider_id INTEGER NOT NULL REFERENCES providers(id),
    field_mapping JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(from_provider_id, to_provider_id)
);

-- Schema validation rules
CREATE TABLE validation_rules (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER NOT NULL REFERENCES providers(id),
    rule_name VARCHAR(100) NOT NULL,
    rule_type VARCHAR(50) NOT NULL, -- 'required', 'optional', 'format', 'custom'
    rule_definition JSONB NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(provider_id, rule_name)
);

-- API usage tracking
CREATE TABLE api_usage (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER NOT NULL REFERENCES providers(id),
    tool_id INTEGER REFERENCES tools(id),
    request_type VARCHAR(50) NOT NULL, -- 'convert', 'validate', 'search'
    request_data JSONB,
    response_status INTEGER,
    response_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_tools_name ON tools(name);
CREATE INDEX idx_tools_category ON tools(category_id);
CREATE INDEX idx_tools_tags ON tools USING GIN(tags);
CREATE INDEX idx_tools_schema ON tools USING GIN(standardized_schema);
CREATE INDEX idx_provider_schemas_tool ON provider_schemas(tool_id);
CREATE INDEX idx_provider_schemas_provider ON provider_schemas(provider_id);
CREATE INDEX idx_tool_examples_tool ON tool_examples(tool_id);
CREATE INDEX idx_tool_examples_provider ON tool_examples(provider_id);
CREATE INDEX idx_api_usage_provider ON api_usage(provider_id);
CREATE INDEX idx_api_usage_created ON api_usage(created_at);

-- Insert initial providers
INSERT INTO providers (name, display_name, description, documentation_url) VALUES
('openai', 'OpenAI', 'OpenAI API with function calling capabilities', 'https://platform.openai.com/docs/api-reference/function-calling'),
('claude', 'Anthropic Claude', 'Anthropic Claude API with tool use capabilities', 'https://docs.claude.com/claude/docs/tool-use'),
('gemini', 'Google Gemini', 'Google Gemini API with function calling', 'https://ai.google.dev/gemini-api/docs/function-calling'),
('mistral', 'Mistral AI', 'Mistral API with function calling support', 'https://docs.mistral.ai/capabilities/function_calling/'),
('cohere', 'Cohere', 'Cohere API with tool use capabilities', 'https://docs.cohere.com/docs/tool-use');

-- Insert initial categories
INSERT INTO categories (name, description) VALUES
('utilities', 'General utility functions'),
('data_access', 'Database and data access tools'),
('web', 'Web scraping and HTTP tools'),
('file_system', 'File system operations'),
('communication', 'Email, messaging, and communication tools'),
('calculation', 'Mathematical and calculation tools'),
('search', 'Search and information retrieval'),
('api', 'API integration and external services'),
('development', 'Development and programming tools'),
('business', 'Business and productivity tools');