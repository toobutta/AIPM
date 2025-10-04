"""
MCP Server implementation for AI Tools Database with Supabase integration
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, CallToolResult, GetResourceRequest, GetResourceResult,
    ListResourcesRequest, ListResourcesResult, ListToolsRequest, ListToolsResult
)
from supabase import create_client, Client
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-tools-mcp")

class AIToolsMCPServer:
    """MCP Server for AI Tools Database with Supabase integration"""

    def __init__(self):
        self.server = Server("ai-tools-database")
        self.supabase: Optional[Client] = None
        self._setup_supabase()
        self._register_handlers()

    def _setup_supabase(self):
        """Initialize Supabase client"""
        try:
            if settings.supabase_url and settings.supabase_anon_key:
                self.supabase = create_client(settings.supabase_url, settings.supabase_anon_key)
                logger.info("✅ Supabase client initialized successfully")
            else:
                logger.warning("⚠️ Supabase credentials not found in environment variables")
                logger.info("Please set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")

    def _register_handlers(self):
        """Register MCP server handlers"""

        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="search_ai_tools",
                    description="Search for AI tools and function definitions by query, category, or provider",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query for tool names or descriptions"},
                            "category": {"type": "string", "description": "Filter by category name"},
                            "provider": {"type": "string", "description": "Filter by provider (openai, claude, gemini, mistral, cohere)"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"},
                            "limit": {"type": "integer", "default": 10, "minimum": 1, "maximum": 50, "description": "Maximum number of results"}
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="get_ai_tool",
                    description="Get detailed information about a specific AI tool including its schema",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tool_id": {"type": "integer", "description": "Database ID of the tool"},
                            "tool_name": {"type": "string", "description": "Name of the tool (alternative to tool_id)"}
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="convert_tool_schema",
                    description="Convert an AI tool schema between different provider formats (OpenAI, Claude, Gemini, etc.)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "schema": {"type": "object", "description": "Tool schema to convert"},
                            "source_provider": {"type": "string", "enum": ["openai", "claude", "gemini", "mistral", "cohere"], "description": "Current provider format"},
                            "target_provider": {"type": "string", "enum": ["openai", "claude", "gemini", "mistral", "cohere"], "description": "Target provider format"}
                        },
                        "required": ["schema", "source_provider", "target_provider"]
                    }
                ),
                Tool(
                    name="validate_tool_schema",
                    description="Validate an AI tool schema against provider-specific rules and requirements",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "schema": {"type": "object", "description": "Tool schema to validate"},
                            "provider": {"type": "string", "enum": ["openai", "claude", "gemini", "mistral", "cohere"], "description": "Provider to validate against"},
                            "strict": {"type": "boolean", "default": false, "description": "Enable strict validation mode"}
                        },
                        "required": ["schema", "provider"]
                    }
                ),
                Tool(
                    name="list_providers",
                    description="List all supported AI providers with their capabilities and validation rules",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="list_categories",
                    description="List all tool categories for organizing and browsing tools",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_tool_examples",
                    description="Get usage examples for a specific tool, including input/output samples",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tool_id": {"type": "integer", "description": "Database ID of the tool"},
                            "provider": {"type": "string", "enum": ["openai", "claude", "gemini", "mistral", "cohere"], "description": "Filter examples by provider"}
                        },
                        "required": ["tool_id"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "search_ai_tools":
                    return await self._search_tools(arguments)
                elif name == "get_ai_tool":
                    return await self._get_tool(arguments)
                elif name == "convert_tool_schema":
                    return await self._convert_schema(arguments)
                elif name == "validate_tool_schema":
                    return await self._validate_schema(arguments)
                elif name == "list_providers":
                    return await self._list_providers()
                elif name == "list_categories":
                    return await self._list_categories()
                elif name == "get_tool_examples":
                    return await self._get_tool_examples(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                        isError=True
                    )
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )

        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available resources"""
            return [
                Resource(
                    uri="data://providers",
                    name="AI Providers",
                    description="List of supported AI providers with their capabilities",
                    mimeType="application/json"
                ),
                Resource(
                    uri="data://categories",
                    name="Tool Categories",
                    description="Categories for organizing AI tools",
                    mimeType="application/json"
                ),
                Resource(
                    uri="data://examples",
                    name="Example Tools",
                    description="Pre-built example AI tools with schemas",
                    mimeType="application/json"
                )
            ]

        @self.server.get_resource()
        async def handle_get_resource(uri: str) -> GetResourceResult:
            """Handle resource requests"""
            try:
                if uri == "data://providers":
                    content = await self._get_providers_data()
                elif uri == "data://categories":
                    content = await self._get_categories_data()
                elif uri == "data://examples":
                    content = await self._get_examples_data()
                else:
                    return GetResourceResult(
                        contents=[TextContent(type="text", text=f"Unknown resource: {uri}")]
                    )

                return GetResourceResult(
                    contents=[TextContent(type="text", text=json.dumps(content, indent=2))]
                )
            except Exception as e:
                logger.error(f"Error getting resource {uri}: {e}")
                return GetResourceResult(
                    contents=[TextContent(type="text", text=f"Error: {str(e)}")]
                )

    async def _search_tools(self, args: Dict[str, Any]) -> CallToolResult:
        """Search for AI tools"""
        if not self.supabase:
            return CallToolResult(
                content=[TextContent(type="text", text="Supabase client not initialized")],
                isError=True
            )

        try:
            query = self.supabase.table("tools").select("*")

            # Apply filters
            if "query" in args:
                query = query.or_(f"name.ilike.%{args['query']}%,description.ilike.%{args['query']}%")

            if "category" in args:
                # Join with categories table
                query = query.select("*, categories(*)").eq("categories.name", args["category"])

            if "provider" in args:
                # This would require joining with provider_schemas table
                # For now, we'll return all tools and filter client-side
                pass

            limit = args.get("limit", 10)
            query = query.limit(limit)

            result = query.execute()

            if result.data:
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result.data, indent=2))]
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text="No tools found matching your criteria")]
                )
        except Exception as e:
            logger.error(f"Error searching tools: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error searching tools: {str(e)}")],
                isError=True
            )

    async def _get_tool(self, args: Dict[str, Any]) -> CallToolResult:
        """Get a specific tool"""
        if not self.supabase:
            return CallToolResult(
                content=[TextContent(type="text", text="Supabase client not initialized")],
                isError=True
            )

        try:
            if "tool_id" in args:
                result = self.supabase.table("tools").select("*").eq("id", args["tool_id"]).execute()
            elif "tool_name" in args:
                result = self.supabase.table("tools").select("*").eq("name", args["tool_name"]).execute()
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text="Either tool_id or tool_name must be provided")],
                    isError=True
                )

            if result.data:
                tool = result.data[0]
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(tool, indent=2))]
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text="Tool not found")]
                )
        except Exception as e:
            logger.error(f"Error getting tool: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting tool: {str(e)}")],
                isError=True
            )

    async def _convert_schema(self, args: Dict[str, Any]) -> CallToolResult:
        """Convert tool schema between providers"""
        try:
            from converters import converter

            converted = converter.convert_schema(
                args["schema"],
                args["source_provider"],
                args["target_provider"]
            )

            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps({
                        "source_provider": args["source_provider"],
                        "target_provider": args["target_provider"],
                        "converted_schema": converted
                    }, indent=2)
                )]
            )
        except Exception as e:
            logger.error(f"Error converting schema: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error converting schema: {str(e)}")],
                isError=True
            )

    async def _validate_schema(self, args: Dict[str, Any]) -> CallToolResult:
        """Validate tool schema"""
        try:
            from validators import validator

            result = validator.validate(
                args["schema"],
                args["provider"],
                args.get("strict", False)
            )

            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result.to_dict(), indent=2))]
            )
        except Exception as e:
            logger.error(f"Error validating schema: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error validating schema: {str(e)}")],
                isError=True
            )

    async def _list_providers(self) -> CallToolResult:
        """List all providers"""
        try:
            from converters import converter

            providers_info = {}
            for provider_name in converter.get_supported_providers():
                providers_info[provider_name] = converter.get_provider_info(provider_name)

            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(providers_info, indent=2))]
            )
        except Exception as e:
            logger.error(f"Error listing providers: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error listing providers: {str(e)}")],
                isError=True
            )

    async def _list_categories(self) -> CallToolResult:
        """List all categories"""
        if not self.supabase:
            return CallToolResult(
                content=[TextContent(type="text", text="Supabase client not initialized")],
                isError=True
            )

        try:
            result = self.supabase.table("categories").select("*").execute()
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result.data, indent=2))]
            )
        except Exception as e:
            logger.error(f"Error listing categories: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error listing categories: {str(e)}")],
                isError=True
            )

    async def _get_tool_examples(self, args: Dict[str, Any]) -> CallToolResult:
        """Get tool examples"""
        if not self.supabase:
            return CallToolResult(
                content=[TextContent(type="text", text="Supabase client not initialized")],
                isError=True
            )

        try:
            query = self.supabase.table("tool_examples").select("*").eq("tool_id", args["tool_id"])

            if "provider" in args:
                # Get provider ID first
                provider_result = self.supabase.table("providers").select("id").eq("name", args["provider"]).execute()
                if provider_result.data:
                    query = query.eq("provider_id", provider_result.data[0]["id"])

            result = query.execute()
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result.data, indent=2))]
            )
        except Exception as e:
            logger.error(f"Error getting tool examples: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting tool examples: {str(e)}")],
                isError=True
            )

    async def _get_providers_data(self) -> Dict[str, Any]:
        """Get providers data for resource endpoint"""
        try:
            from converters import converter
            providers_info = {}
            for provider_name in converter.get_supported_providers():
                providers_info[provider_name] = converter.get_provider_info(provider_name)
            return providers_info
        except Exception as e:
            logger.error(f"Error getting providers data: {e}")
            return {"error": str(e)}

    async def _get_categories_data(self) -> List[Dict[str, Any]]:
        """Get categories data for resource endpoint"""
        if not self.supabase:
            return [{"error": "Supabase client not initialized"}]

        try:
            result = self.supabase.table("categories").select("*").execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting categories data: {e}")
            return [{"error": str(e)}]

    async def _get_examples_data(self) -> Dict[str, Any]:
        """Get examples data for resource endpoint"""
        try:
            from examples import EXAMPLE_TOOLS, PROVIDER_EXAMPLES
            return {
                "tools": EXAMPLE_TOOLS,
                "conversions": PROVIDER_EXAMPLES
            }
        except Exception as e:
            logger.error(f"Error getting examples data: {e}")
            return {"error": str(e)}

    async def run(self):
        """Run the MCP server"""
        # Use stdio transport
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ai-tools-database",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={}
                    )
                )
            )

async def main():
    """Main entry point"""
    server = AIToolsMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())