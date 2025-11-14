"""
Tool Integration Framework for Galion Platform v2.2
Provides Manus-like tool integration capabilities for agents.

Features:
- Extensible tool registry
- Standardized tool interfaces
- Authentication and security
- Tool discovery and metadata
- Cost tracking and rate limiting
- Error handling and retry logic

"Your imagination is the end."
"""

import asyncio
from typing import Dict, List, Optional, Any, Union, Callable, Type
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
import aiohttp
import requests
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ToolCategory(Enum):
    """Categories of tools"""
    WEB_SEARCH = "web_search"
    API_INTEGRATION = "api_integration"
    FILE_SYSTEM = "file_system"
    DATABASE = "database"
    COMMUNICATION = "communication"
    PRODUCTIVITY = "productivity"
    DEVELOPMENT = "development"
    ANALYTICS = "analytics"
    SOCIAL_MEDIA = "social_media"
    FINANCIAL = "financial"

class ToolResult(BaseModel):
    """Standardized result from tool execution"""

    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_time: float = 0.0
    cost: float = 0.0
    rate_limit_remaining: Optional[int] = None

class ToolParameter(BaseModel):
    """Parameter definition for a tool"""

    name: str
    type: str  # "string", "number", "boolean", "object", "array"
    description: str
    required: bool = False
    default: Any = None
    enum: Optional[List[Any]] = None
    schema: Optional[Dict[str, Any]] = None  # JSON schema for complex types

class ToolMetadata(BaseModel):
    """Metadata about a tool"""

    name: str
    description: str
    category: ToolCategory
    version: str = "1.0.0"
    author: str = "Galion Platform"
    tags: List[str] = Field(default_factory=list)
    parameters: List[ToolParameter] = Field(default_factory=list)
    returns: Dict[str, Any] = Field(default_factory=dict)
    cost_per_call: float = 0.0
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    authentication_required: bool = False
    requires_approval: bool = False
    is_deprecated: bool = False

class BaseTool(ABC):
    """
    Base class for all tools in the framework.

    Tools provide standardized interfaces for external service integration.
    """

    def __init__(self, metadata: ToolMetadata):
        self.metadata = metadata
        self.logger = logging.getLogger(f"{__name__}.{self.metadata.name}")

        # Rate limiting
        self.call_history: List[datetime] = []
        self.rate_limit_lock = asyncio.Lock()

    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute the tool with given parameters.

        Args:
            parameters: Tool-specific parameters

        Returns:
            ToolResult with execution outcome
        """
        pass

    def validate_parameters(self, parameters: Dict[str, Any]) -> List[str]:
        """Validate input parameters against tool metadata"""
        errors = []

        # Check required parameters
        for param in self.metadata.parameters:
            if param.required and param.name not in parameters:
                errors.append(f"Missing required parameter: {param.name}")

        # Type validation (basic)
        for param in self.metadata.parameters:
            if param.name in parameters:
                value = parameters[param.name]

                # Basic type checking
                if param.type == "string" and not isinstance(value, str):
                    errors.append(f"Parameter {param.name} must be a string")
                elif param.type == "number" and not isinstance(value, (int, float)):
                    errors.append(f"Parameter {param.name} must be a number")
                elif param.type == "boolean" and not isinstance(value, bool):
                    errors.append(f"Parameter {param.name} must be a boolean")
                elif param.type == "array" and not isinstance(value, list):
                    errors.append(f"Parameter {param.name} must be an array")

                # Enum validation
                if param.enum and value not in param.enum:
                    errors.append(f"Parameter {param.name} must be one of: {param.enum}")

        return errors

    async def check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        async with self.rate_limit_lock:
            now = datetime.now()

            # Clean old entries
            cutoff_minute = now - timedelta(minutes=1)
            cutoff_hour = now - timedelta(hours=1)

            self.call_history = [
                call_time for call_time in self.call_history
                if call_time > cutoff_hour
            ]

            # Check limits
            calls_last_minute = sum(1 for t in self.call_history if t > cutoff_minute)
            calls_last_hour = len(self.call_history)

            if (self.metadata.rate_limit_per_minute and
                calls_last_minute >= self.metadata.rate_limit_per_minute):
                return False

            if (self.metadata.rate_limit_per_hour and
                calls_last_hour >= self.metadata.rate_limit_per_hour):
                return False

            # Record this call
            self.call_history.append(now)
            return True

    def get_status(self) -> Dict[str, Any]:
        """Get tool status and metadata"""
        return {
            "name": self.metadata.name,
            "category": self.metadata.category.value,
            "version": self.metadata.version,
            "calls_last_hour": len([
                t for t in self.call_history
                if t > datetime.now() - timedelta(hours=1)
            ]),
            "rate_limit_per_minute": self.metadata.rate_limit_per_minute,
            "rate_limit_per_hour": self.metadata.rate_limit_per_hour,
            "authentication_required": self.metadata.authentication_required,
            "requires_approval": self.metadata.requires_approval,
            "is_deprecated": self.metadata.is_deprecated
        }

class WebSearchTool(BaseTool):
    """Tool for web search functionality"""

    def __init__(self, api_key: str, search_engine: str = "google"):
        metadata = ToolMetadata(
            name="web_search",
            description="Search the web for information",
            category=ToolCategory.WEB_SEARCH,
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="Search query",
                    required=True
                ),
                ToolParameter(
                    name="num_results",
                    type="number",
                    description="Number of results to return",
                    default=5
                )
            ],
            returns={"type": "array", "description": "List of search results"},
            cost_per_call=0.01,
            rate_limit_per_minute=30
        )

        super().__init__(metadata)
        self.api_key = api_key
        self.search_engine = search_engine

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = datetime.now()

        # Validate rate limit
        if not await self.check_rate_limit():
            return ToolResult(
                success=False,
                error="Rate limit exceeded",
                execution_time=(datetime.now() - start_time).total_seconds()
            )

        # Validate parameters
        errors = self.validate_parameters(parameters)
        if errors:
            return ToolResult(
                success=False,
                error=f"Parameter validation failed: {', '.join(errors)}",
                execution_time=(datetime.now() - start_time).total_seconds()
            )

        try:
            query = parameters["query"]
            num_results = parameters.get("num_results", 5)

            # Simulate web search (replace with actual API call)
            results = await self._perform_search(query, num_results)

            execution_time = (datetime.now() - start_time).total_seconds()

            return ToolResult(
                success=True,
                data=results,
                execution_time=execution_time,
                cost=self.metadata.cost_per_call
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ToolResult(
                success=False,
                error=f"Search failed: {str(e)}",
                execution_time=execution_time,
                cost=self.metadata.cost_per_call
            )

    async def _perform_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Perform the actual web search"""
        # This is a placeholder - integrate with actual search APIs
        # like Google Custom Search, Bing Web Search, etc.

        # For now, return mock results
        return [
            {
                "title": f"Result {i+1} for '{query}'",
                "url": f"https://example.com/result{i+1}",
                "snippet": f"This is a sample search result snippet for the query '{query}'. It contains relevant information.",
                "relevance_score": 0.9 - (i * 0.1)
            }
            for i in range(min(num_results, 5))
        ]

class HTTPApiTool(BaseTool):
    """Generic tool for HTTP API calls"""

    def __init__(self, name: str, base_url: str, auth_token: Optional[str] = None):
        metadata = ToolMetadata(
            name=name,
            description=f"API integration for {name}",
            category=ToolCategory.API_INTEGRATION,
            parameters=[
                ToolParameter(
                    name="method",
                    type="string",
                    description="HTTP method",
                    enum=["GET", "POST", "PUT", "DELETE"],
                    default="GET"
                ),
                ToolParameter(
                    name="endpoint",
                    type="string",
                    description="API endpoint path",
                    required=True
                ),
                ToolParameter(
                    name="data",
                    type="object",
                    description="Request data for POST/PUT",
                    default={}
                ),
                ToolParameter(
                    name="headers",
                    type="object",
                    description="Additional headers",
                    default={}
                )
            ],
            returns={"type": "object", "description": "API response"},
            cost_per_call=0.02,
            authentication_required=auth_token is not None
        )

        super().__init__(metadata)
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = datetime.now()

        # Validate rate limit
        if not await self.check_rate_limit():
            return ToolResult(
                success=False,
                error="Rate limit exceeded",
                execution_time=(datetime.now() - start_time).total_seconds()
            )

        errors = self.validate_parameters(parameters)
        if errors:
            return ToolResult(
                success=False,
                error=f"Parameter validation failed: {', '.join(errors)}",
                execution_time=(datetime.now() - start_time).total_seconds()
            )

        try:
            method = parameters.get("method", "GET")
            endpoint = parameters["endpoint"]
            data = parameters.get("data", {})
            headers = parameters.get("headers", {})

            # Add authentication if available
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"

            url = f"{self.base_url}/{endpoint.lstrip('/')}"

            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, headers=headers) as response:
                        result_data = await response.json()
                        status_code = response.status
                elif method == "POST":
                    async with session.post(url, json=data, headers=headers) as response:
                        result_data = await response.json()
                        status_code = response.status
                elif method == "PUT":
                    async with session.put(url, json=data, headers=headers) as response:
                        result_data = await response.json()
                        status_code = response.status
                elif method == "DELETE":
                    async with session.delete(url, headers=headers) as response:
                        result_data = await response.json() if response.content_type == 'application/json' else {}
                        status_code = response.status
                else:
                    raise ValueError(f"Unsupported method: {method}")

            execution_time = (datetime.now() - start_time).total_seconds()

            return ToolResult(
                success=status_code < 400,
                data=result_data,
                metadata={"status_code": status_code, "url": url},
                execution_time=execution_time,
                cost=self.metadata.cost_per_call
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ToolResult(
                success=False,
                error=f"API call failed: {str(e)}",
                execution_time=execution_time,
                cost=self.metadata.cost_per_call
            )

class ToolRegistry:
    """
    Registry for managing available tools.

    Provides discovery, registration, and execution of tools.
    """

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.categories: Dict[ToolCategory, List[str]] = {}
        self.logger = logging.getLogger(f"{__name__}.registry")

    def register_tool(self, tool: BaseTool) -> bool:
        """Register a tool in the registry"""
        if tool.metadata.name in self.tools:
            self.logger.warning(f"Tool {tool.metadata.name} already registered")
            return False

        self.tools[tool.metadata.name] = tool

        # Add to category index
        if tool.metadata.category not in self.categories:
            self.categories[tool.metadata.category] = []
        self.categories[tool.metadata.category].append(tool.metadata.name)

        self.logger.info(f"Registered tool: {tool.metadata.name}")
        return True

    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool"""
        if tool_name not in self.tools:
            return False

        tool = self.tools[tool_name]
        del self.tools[tool_name]

        # Remove from category index
        if tool.metadata.category in self.categories:
            self.categories[tool.metadata.category] = [
                name for name in self.categories[tool.metadata.category]
                if name != tool_name
            ]

        self.logger.info(f"Unregistered tool: {tool_name}")
        return True

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(tool_name)

    def list_tools(self, category: Optional[ToolCategory] = None) -> List[Dict[str, Any]]:
        """List available tools, optionally filtered by category"""
        if category:
            tool_names = self.categories.get(category, [])
        else:
            tool_names = list(self.tools.keys())

        return [
            {
                "name": name,
                "metadata": self.tools[name].metadata.model_dump(),
                "status": self.tools[name].get_status()
            }
            for name in tool_names
        ]

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> ToolResult:
        """Execute a tool with given parameters"""
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' not found",
                execution_time=0.0
            )

        return await tool.execute(parameters)

    def search_tools(self, query: str, category: Optional[ToolCategory] = None) -> List[Dict[str, Any]]:
        """Search for tools by name, description, or tags"""
        query_lower = query.lower()
        matching_tools = []

        tool_names = self.categories.get(category, list(self.tools.keys())) if category else list(self.tools.keys())

        for name in tool_names:
            tool = self.tools[name]
            metadata = tool.metadata

            # Search in name, description, and tags
            searchable_text = f"{metadata.name} {metadata.description} {' '.join(metadata.tags)}".lower()

            if query_lower in searchable_text:
                matching_tools.append({
                    "name": name,
                    "metadata": metadata.model_dump(),
                    "status": tool.get_status()
                })

        return matching_tools

    def get_registry_status(self) -> Dict[str, Any]:
        """Get registry status and statistics"""
        total_tools = len(self.tools)
        tools_by_category = {
            category.value: len(tools) for category, tools in self.categories.items()
        }

        return {
            "total_tools": total_tools,
            "categories": tools_by_category,
            "tools": list(self.tools.keys())
        }

class ToolManager:
    """
    High-level manager for tool operations.

    Provides convenient interfaces for tool discovery and execution.
    """

    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.logger = logging.getLogger(f"{__name__}.manager")

    async def discover_tools(self, query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Discover tools based on a natural language query.

        Uses context and query analysis to find relevant tools.
        """
        # Simple keyword-based discovery for now
        # Could be enhanced with NLP for better matching

        tools = self.registry.search_tools(query)

        # Add relevance scoring based on context
        if context:
            for tool_info in tools:
                relevance = self._calculate_relevance(tool_info, query, context)
                tool_info["relevance_score"] = relevance

            # Sort by relevance
            tools.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        return tools

    def _calculate_relevance(self, tool_info: Dict[str, Any], query: str, context: Dict[str, Any]) -> float:
        """Calculate relevance score for a tool"""
        score = 0.0
        metadata = tool_info["metadata"]

        # Category matching based on context
        if "task_type" in context:
            task_type = context["task_type"].lower()
            if task_type in metadata["category"]:
                score += 0.5

        # Keyword matching
        query_words = set(query.lower().split())
        description_words = set(metadata["description"].lower().split())
        tag_words = set(tag.lower() for tag in metadata.get("tags", []))

        all_words = description_words | tag_words
        matching_words = query_words & all_words

        score += len(matching_words) * 0.1

        return min(score, 1.0)  # Cap at 1.0

    async def execute_tool_chain(
        self,
        tool_chain: List[Dict[str, Any]],
        initial_data: Dict[str, Any] = None
    ) -> List[ToolResult]:
        """
        Execute a chain of tools, passing data between them.

        Args:
            tool_chain: List of {"tool": name, "parameters": {...}} dicts
            initial_data: Initial data to pass to first tool

        Returns:
            List of ToolResults for each step
        """
        results = []
        current_data = initial_data or {}

        for step in tool_chain:
            tool_name = step["tool"]
            parameters = step.get("parameters", {}).copy()

            # Merge current data with step parameters
            for key, value in current_data.items():
                if key not in parameters:
                    parameters[key] = value

            result = await self.registry.execute_tool(tool_name, parameters)
            results.append(result)

            if not result.success:
                self.logger.error(f"Tool chain failed at step: {tool_name}")
                break

            # Update current data with result
            if result.data:
                current_data.update(result.data)

        return results

    def create_tool_from_config(self, config: Dict[str, Any]) -> Optional[BaseTool]:
        """Create a tool instance from configuration"""
        tool_type = config.get("type")

        if tool_type == "web_search":
            return WebSearchTool(
                api_key=config.get("api_key", ""),
                search_engine=config.get("search_engine", "google")
            )
        elif tool_type == "http_api":
            return HTTPApiTool(
                name=config["name"],
                base_url=config["base_url"],
                auth_token=config.get("auth_token")
            )

        self.logger.warning(f"Unknown tool type: {tool_type}")
        return None

    async def load_tools_from_config(self, config_file: str):
        """Load tools from a configuration file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            for tool_config in config.get("tools", []):
                tool = self.create_tool_from_config(tool_config)
                if tool:
                    self.registry.register_tool(tool)

            self.logger.info(f"Loaded tools from {config_file}")

        except Exception as e:
            self.logger.error(f"Failed to load tools from config: {e}")

# Pre-configured tool factory
def create_default_tool_registry() -> ToolRegistry:
    """Create a registry with default tools"""
    registry = ToolRegistry()

    # Add a basic web search tool (placeholder)
    search_tool = WebSearchTool(api_key="placeholder")
    registry.register_tool(search_tool)

    return registry
