#!/usr/bin/env python3
"""
Test script for MCP Server functionality
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server import AIToolsMCPServer
from config import settings

class MCPTester:
    """Test suite for MCP Server"""

    def __init__(self):
        self.server = AIToolsMCPServer()

    async def test_supabase_connection(self):
        """Test Supabase connection"""
        print("🔍 Testing Supabase connection...")

        if not self.server.supabase:
            print("❌ Supabase client not initialized")
            print("   Please check your environment variables:")
            print("   - SUPABASE_URL")
            print("   - SUPABASE_ANON_KEY")
            return False

        try:
            # Test basic query
            result = self.server.supabase.table("providers").select("count").execute()
            print("✅ Supabase connection successful")
            return True
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            return False

    async def test_provider_listing(self):
        """Test provider listing functionality"""
        print("\n📋 Testing provider listing...")

        try:
            result = await self.server._list_providers({})
            print("✅ Provider listing successful")

            # Parse and display providers
            data = json.loads(result.content[0].text)
            for provider, info in data.items():
                print(f"   - {provider}: {info.get('display_name', 'Unknown')}")

            return True
        except Exception as e:
            print(f"❌ Provider listing failed: {e}")
            return False

    async def test_tool_search(self):
        """Test tool search functionality"""
        print("\n🔍 Testing tool search...")

        try:
            result = await self.server._search_tools({"query": "weather", "limit": 3})
            print("✅ Tool search successful")

            # Parse and display results
            data = json.loads(result.content[0].text)
            if isinstance(data, list):
                print(f"   Found {len(data)} tools:")
                for tool in data[:3]:  # Show first 3
                    print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:50]}...")
            else:
                print(f"   Result: {data}")

            return True
        except Exception as e:
            print(f"❌ Tool search failed: {e}")
            return False

    async def test_schema_conversion(self):
        """Test schema conversion functionality"""
        print("\n🔄 Testing schema conversion...")

        try:
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

            result = await self.server._convert_schema({
                "schema": claude_schema,
                "source_provider": "claude",
                "target_provider": "openai"
            })

            print("✅ Schema conversion successful")

            # Parse and display result
            data = json.loads(result.content[0].text)
            print(f"   Converted from {data['source_provider']} to {data['target_provider']}")

            converted_schema = data["converted_schema"]
            print(f"   Has 'parameters' field: {'parameters' in converted_schema}")
            print(f"   Has 'input_schema' field: {'input_schema' in converted_schema}")

            return True
        except Exception as e:
            print(f"❌ Schema conversion failed: {e}")
            return False

    async def test_schema_validation(self):
        """Test schema validation functionality"""
        print("\n✅ Testing schema validation...")

        try:
            valid_schema = {
                "name": "test_tool",
                "description": "Test tool for validation",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    },
                    "required": ["input"]
                }
            }

            result = await self.server._validate_schema({
                "schema": valid_schema,
                "provider": "claude",
                "strict": False
            })

            print("✅ Schema validation successful")

            # Parse and display result
            data = json.loads(result.content[0].text)
            print(f"   Valid: {data['is_valid']}")
            print(f"   Errors: {data['error_count']}")
            print(f"   Warnings: {data['warning_count']}")

            return True
        except Exception as e:
            print(f"❌ Schema validation failed: {e}")
            return False

    async def test_categories(self):
        """Test categories functionality"""
        print("\n📂 Testing categories...")

        try:
            result = await self.server._list_categories({})
            print("✅ Categories listing successful")

            # Parse and display categories
            data = json.loads(result.content[0].text)
            if isinstance(data, list):
                print(f"   Found {len(data)} categories:")
                for category in data[:5]:  # Show first 5
                    print(f"   - {category.get('name', 'Unknown')}")

            return True
        except Exception as e:
            print(f"❌ Categories listing failed: {e}")
            return False

    async def test_resources(self):
        """Test resource endpoints"""
        print("\n📚 Testing resources...")

        resources = ["data://providers", "data://categories", "data://examples"]

        for resource in resources:
            try:
                content = await self.server._get_resource_data(resource)
                print(f"   ✅ {resource}: Data retrieved")
            except Exception as e:
                print(f"   ❌ {resource}: {e}")
                return False

        print("✅ All resources tested successfully")
        return True

    async def _get_resource_data(self, uri):
        """Helper method to get resource data"""
        if uri == "data://providers":
            return await self.server._get_providers_data()
        elif uri == "data://categories":
            return await self.server._get_categories_data()
        elif uri == "data://examples":
            return await self.server._get_examples_data()
        else:
            raise ValueError(f"Unknown resource: {uri}")

    async def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting MCP Server Tests")
        print("=" * 50)

        tests = [
            self.test_supabase_connection,
            self.test_provider_listing,
            self.test_categories,
            self.test_tool_search,
            self.test_schema_conversion,
            self.test_schema_validation,
            self.test_resources
        ]

        passed = 0
        total = len(tests)

        for test in tests:
            try:
                if await test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")

        print("\n" + "=" * 50)
        print(f"🎯 Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! MCP Server is ready to use.")
        else:
            print("⚠️  Some tests failed. Check the configuration and try again.")

        return passed == total

def check_environment():
    """Check if environment is properly configured"""
    print("🔧 Checking environment configuration...")

    required_vars = ["DATABASE_URL", "SUPABASE_URL", "SUPABASE_ANON_KEY"]
    missing = []

    for var in required_vars:
        if not getattr(settings, var.lower(), None):
            missing.append(var)

    if missing:
        print("❌ Missing environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease update your .env file with the required variables.")
        return False

    print("✅ Environment variables are configured")
    return True

async def main():
    """Main test runner"""
    print("🚀 AI Tools Database - MCP Server Test Suite")
    print("=" * 60)

    # Check environment first
    if not check_environment():
        sys.exit(1)

    # Run tests
    tester = MCPTester()
    success = await tester.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())