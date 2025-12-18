"""
MCP Client for browser interaction
"""
import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp import ClientSession
from mcp.client.sse import sse_client
from ..config.logger import get_logger
from ..config.config import config

logger = get_logger(__name__)

class MCPPlaywrightClient:
    """Client to interact with Playwright MCP server"""
    
    def __init__(self, host: str = "mcp-playwright", port: int = 3001):
        self.url = f"http://{host}:{port}/sse"
        self.session: Optional[ClientSession] = None
        self._exit_stack = None

    async def connect(self):
        """Establish connection to the MCP server"""
        if self.session:
            return
        
        logger.info(f"Connecting to MCP Playwright at {self.url}...")
        try:
            from contextlib import AsyncExitStack
            self._exit_stack = AsyncExitStack()
            
            # Use sse_client transport
            streams = await self._exit_stack.enter_async_context(sse_client(self.url))
            self.session = await self._exit_stack.enter_async_context(ClientSession(streams[0], streams[1]))
            
            # Initialize session
            await self.session.initialize()
            logger.info("MCP Playwright session initialized.")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            self.session = None
            if self._exit_stack:
                await self._exit_stack.aclose()
            raise

    async def disconnect(self):
        """Close the connection"""
        if self._exit_stack:
            await self._exit_stack.aclose()
            self.session = None
            logger.info("MCP Playwright session closed.")

    async def list_tools(self) -> List[Any]:
        """List available tools on the server"""
        if not self.session:
            await self.connect()
        return await self.session.list_tools()

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool on the MCP server"""
        if not self.session:
            await self.connect()
        
        logger.info(f"Calling MCP tool: {name} with args: {arguments}")
        try:
            result = await self.session.call_tool(name, arguments)
            return result
        except Exception as e:
            logger.error(f"Error calling MCP tool {name}: {e}")
            raise

mcp_client = MCPPlaywrightClient()
