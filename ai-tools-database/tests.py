"""
Test suite for AI Tools Database
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

from main import app
from database import get_db, Base
from models import Provider, Category, Tool

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override database dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)

    # Add test data
    db = TestingSessionLocal()

    # Add test provider
    provider = Provider(
        name="openai",
        display_name="OpenAI",
        description="Test provider"
    )
    db.add(provider)

    # Add test category
    category = Category(
        name="test_category",
        description="Test category"
    )
    db.add(category)

    db.commit()

    yield

    # Cleanup
    Base.metadata.drop_all(bind=engine)

class TestHealth:
    """Test health check endpoint"""

    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "supported_providers" in data

class TestProviders:
    """Test provider endpoints"""

    def test_get_providers(self):
        response = client.get("/api/providers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["name"] == "openai"

    def test_get_provider_info(self):
        response = client.get("/api/providers/openai/info")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "openai"
        assert "validation_rules" in data
        assert "field_mappings" in data

    def test_get_nonexistent_provider_info(self):
        response = client.get("/api/providers/nonexistent/info")
        assert response.status_code == 404

class TestConversion:
    """Test schema conversion endpoints"""

    def test_convert_claude_to_openai(self):
        claude_schema = {
            "name": "get_weather",
            "description": "Get current weather",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }

        response = client.post("/api/convert", json={
            "source_schema": claude_schema,
            "source_provider": "claude",
            "target_provider": "openai"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "target_schema" in data
        assert data["target_schema"]["name"] == "get_weather"
        assert "parameters" in data["target_schema"]
        assert "input_schema" not in data["target_schema"]

    def test_convert_invalid_provider(self):
        response = client.post("/api/convert", json={
            "source_schema": {},
            "source_provider": "invalid",
            "target_provider": "openai"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "error" in data

class TestValidation:
    """Test schema validation endpoints"""

    def test_validate_valid_schema(self):
        valid_schema = {
            "name": "get_weather",
            "description": "Get current weather",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }

        response = client.post("/api/validate", json={
            "schema": valid_schema,
            "provider": "claude",
            "strict": False
        })

        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["error_count"] == 0

    def test_validate_invalid_schema(self):
        invalid_schema = {
            "name": "get_weather",
            "description": "Get current weather"
            # Missing input_schema
        }

        response = client.post("/api/validate", json={
            "schema": invalid_schema,
            "provider": "claude",
            "strict": False
        })

        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert data["error_count"] > 0

    def test_batch_validation(self):
        schemas = [
            {
                "name": "tool1",
                "description": "Tool 1",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "tool2",
                "description": "Tool 2"
                # Invalid: missing input_schema
            }
        ]

        response = client.post("/api/validate/batch", json={
            "schemas": schemas,
            "providers": ["claude", "claude"],
            "strict": False
        })

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "summary" in data
        assert len(data["results"]) == 2

class TestTools:
    """Test tool management endpoints"""

    def test_search_tools(self):
        response = client.get("/api/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert "total" in data
        assert isinstance(data["tools"], list)

    def test_create_tool(self):
        tool_data = {
            "name": "test_tool",
            "description": "Test tool for API testing",
            "category_id": 1,
            "standardized_schema": {
                "name": "test_tool",
                "description": "Test tool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    },
                    "required": ["input"]
                }
            },
            "tags": ["test", "api"]
        }

        response = client.post("/api/tools", json=tool_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test_tool"
        assert "id" in data

        return data["id"]

    def test_get_tool(self, setup_database):
        # First create a tool
        create_response = client.post("/api/tools", json={
            "name": "get_tool_test",
            "description": "Test get tool",
            "category_id": 1,
            "standardized_schema": {
                "name": "get_tool_test",
                "description": "Test",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        })

        tool_id = create_response.json()["id"]

        # Get the tool
        response = client.get(f"/api/tools/{tool_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "get_tool_test"

    def test_get_nonexistent_tool(self):
        response = client.get("/api/tools/99999")
        assert response.status_code == 404

    def test_update_tool(self):
        # Create a tool first
        create_response = client.post("/api/tools", json={
            "name": "update_test",
            "description": "Original description",
            "category_id": 1,
            "standardized_schema": {
                "name": "update_test",
                "description": "Original",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        })

        tool_id = create_response.json()["id"]

        # Update the tool
        response = client.put(f"/api/tools/{tool_id}", json={
            "description": "Updated description"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    def test_delete_tool(self):
        # Create a tool first
        create_response = client.post("/api/tools", json={
            "name": "delete_test",
            "description": "Tool to delete",
            "category_id": 1,
            "standardized_schema": {
                "name": "delete_test",
                "description": "Delete me",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        })

        tool_id = create_response.json()["id"]

        # Delete the tool
        response = client.delete(f"/api/tools/{tool_id}")
        assert response.status_code == 200

        # Verify it's deleted
        get_response = client.get(f"/api/tools/{tool_id}")
        assert get_response.status_code == 404

class TestExamples:
    """Test example endpoints"""

    def test_get_conversion_examples(self):
        response = client.get("/api/examples")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "claude_to_openai" in data

    def test_get_tool_example(self):
        response = client.get("/api/examples/weather?provider=openai")
        assert response.status_code == 200
        data = response.json()
        assert data["tool_name"] == "weather"
        assert data["provider"] == "openai"
        assert "schema" in data

    def test_get_nonexistent_example(self):
        response = client.get("/api/examples/nonexistent?provider=openai")
        assert response.status_code == 404

class TestToolSchemas:
    """Test tool schema endpoints"""

    def test_get_tool_schemas(self):
        # Create a tool first
        tool_response = client.post("/api/tools", json={
            "name": "schema_test",
            "description": "Tool for schema testing",
            "category_id": 1,
            "standardized_schema": {
                "name": "schema_test",
                "description": "Schema test",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        })

        tool_id = tool_response.json()["id"]

        # Get schemas for the tool
        response = client.get(f"/api/tools/{tool_id}/schemas")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_tool_schema(self):
        # Create a tool first
        tool_response = client.post("/api/tools", json={
            "name": "schema_create_test",
            "description": "Tool for schema creation testing",
            "category_id": 1,
            "standardized_schema": {
                "name": "schema_create_test",
                "description": "Schema create test",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        })

        tool_id = tool_response.json()["id"]

        # Create a provider schema
        response = client.post(f"/api/tools/{tool_id}/schemas", json={
            "provider_id": 1,
            "schema_format": {
                "name": "schema_create_test",
                "description": "Test schema",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "is_supported": True
        })

        assert response.status_code == 200
        data = response.json()
        assert data["tool_id"] == tool_id
        assert data["provider_id"] == 1

class TestToolExamples:
    """Test tool example endpoints"""

    def test_get_tool_examples(self):
        # Create a tool first
        tool_response = client.post("/api/tools", json={
            "name": "example_test",
            "description": "Tool for example testing",
            "category_id": 1,
            "standardized_schema": {
                "name": "example_test",
                "description": "Example test",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        })

        tool_id = tool_response.json()["id"]

        # Get examples for the tool
        response = client.get(f"/api/tools/{tool_id}/examples")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_tool_example(self):
        # Create a tool first
        tool_response = client.post("/api/tools", json={
            "name": "example_create_test",
            "description": "Tool for example creation testing",
            "category_id": 1,
            "standardized_schema": {
                "name": "example_create_test",
                "description": "Example create test",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        })

        tool_id = tool_response.json()["id"]

        # Create an example
        response = client.post(f"/api/tools/{tool_id}/examples", json={
            "provider_id": 1,
            "example_name": "test_example",
            "description": "Test example description",
            "input_data": {"test": "input"},
            "expected_output": {"result": "success"}
        })

        assert response.status_code == 200
        data = response.json()
        assert data["tool_id"] == tool_id
        assert data["example_name"] == "test_example"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])