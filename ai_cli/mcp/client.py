import asyncio
from typing import Dict, List, Any, Optional
import httpx

# MCP imports - optional for now
try:
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    ClientSession = None
    stdio_client = None
    MCP_AVAILABLE = False


class MCPClient:
    def __init__(self):
        if not MCP_AVAILABLE:
            raise ImportError("MCP not available. Install with: pip install mcp")
        self.sessions: Dict[str, Any] = {}
        self.connections: Dict[str, Any] = {}

    async def connect_gitlab(
        self, 
        auth_token: str, 
        base_url: str = "https://gitlab.com"
    ) -> None:
        server_params = {
            "command": "python",
            "args": ["-m", "ai_cli.mcp.gitlab_server"],
            "env": {
                "GITLAB_TOKEN": auth_token,
                "GITLAB_BASE_URL": base_url
            }
        }
        
        read, write = await stdio_client(server_params)
        session = ClientSession(read, write)
        
        await session.initialize()
        
        self.sessions["gitlab"] = session
        self.connections["gitlab"] = {
            "read": read,
            "write": write,
            "auth_token": auth_token,
            "base_url": base_url
        }

    async def connect_github(
        self, 
        auth_token: str, 
        base_url: str = "https://api.github.com"
    ) -> None:
        server_params = {
            "command": "python",
            "args": ["-m", "ai_cli.mcp.github_server"],
            "env": {
                "GITHUB_TOKEN": auth_token,
                "GITHUB_BASE_URL": base_url
            }
        }
        
        read, write = await stdio_client(server_params)
        session = ClientSession(read, write)
        
        await session.initialize()
        
        self.sessions["github"] = session
        self.connections["github"] = {
            "read": read,
            "write": write,
            "auth_token": auth_token,
            "base_url": base_url
        }

    async def list_resources(self, service: str) -> List[Dict[str, Any]]:
        if service not in self.sessions:
            raise ValueError(f"No connection to {service}")
        
        session = self.sessions[service]
        result = await session.list_resources()
        return result.resources

    async def read_resource(
        self, 
        service: str, 
        uri: str
    ) -> Dict[str, Any]:
        if service not in self.sessions:
            raise ValueError(f"No connection to {service}")
        
        session = self.sessions[service]
        result = await session.read_resource(uri)
        return result.contents[0] if result.contents else {}

    async def list_tools(self, service: str) -> List[Dict[str, Any]]:
        if service not in self.sessions:
            raise ValueError(f"No connection to {service}")
        
        session = self.sessions[service]
        result = await session.list_tools()
        return result.tools

    async def call_tool(
        self, 
        service: str, 
        tool_name: str, 
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        if service not in self.sessions:
            raise ValueError(f"No connection to {service}")
        
        session = self.sessions[service]
        result = await session.call_tool(tool_name, arguments)
        return result.content[0] if result.content else {}

    async def get_repository_files(
        self, 
        service: str, 
        owner: str, 
        repo: str,
        path: str = ""
    ) -> List[Dict[str, Any]]:
        uri = f"{service}://{owner}/{repo}/files/{path}"
        return await self.read_resource(service, uri)

    async def get_file_content(
        self, 
        service: str, 
        owner: str, 
        repo: str,
        file_path: str
    ) -> str:
        result = await self.call_tool(
            service,
            "get_file_content",
            {
                "owner": owner,
                "repo": repo,
                "path": file_path
            }
        )
        return result.get("content", "")

    async def search_code(
        self, 
        service: str, 
        query: str,
        owner: Optional[str] = None,
        repo: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        arguments = {"query": query}
        if owner:
            arguments["owner"] = owner
        if repo:
            arguments["repo"] = repo
            
        result = await self.call_tool(service, "search_code", arguments)
        return result.get("results", [])

    async def close_all(self) -> None:
        for service, connection in self.connections.items():
            try:
                if "write" in connection:
                    connection["write"].close()
                if "read" in connection:
                    connection["read"].close()
            except Exception:
                pass
        
        self.sessions.clear()
        self.connections.clear()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_all()