import os
import asyncio
from typing import Dict, List, Any, Optional
import httpx

try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    FastMCP = None
    MCP_AVAILABLE = False


class GitLabMCPServer:
    def __init__(self):
        if not MCP_AVAILABLE:
            raise ImportError("MCP not available. Install with: pip install mcp fastmcp")
            
        self.token = os.getenv("GITLAB_TOKEN")
        self.base_url = os.getenv("GITLAB_BASE_URL", "https://gitlab.com")
        self.api_url = f"{self.base_url}/api/v4"
        
        if not self.token:
            raise ValueError("GITLAB_TOKEN environment variable is required")
        
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=30.0
        )
        
        self.mcp = FastMCP("GitLab MCP Server")
        self._setup_resources()
        self._setup_tools()

    def _setup_resources(self):
        @self.mcp.resource("gitlab://projects")
        async def list_projects() -> str:
            response = await self.client.get(f"{self.api_url}/projects")
            response.raise_for_status()
            projects = response.json()
            
            result = "GitLab Projects:\n"
            for project in projects[:10]:  # Limit to first 10
                result += f"- {project['name']} ({project['path_with_namespace']})\n"
                result += f"  URL: {project['web_url']}\n"
                result += f"  Description: {project.get('description', 'No description')}\n\n"
            
            return result

        @self.mcp.resource("gitlab://{owner}/{repo}/files")
        async def list_repository_files(owner: str, repo: str) -> str:
            project_path = f"{owner}/{repo}"
            response = await self.client.get(
                f"{self.api_url}/projects/{project_path.replace('/', '%2F')}/repository/tree"
            )
            response.raise_for_status()
            files = response.json()
            
            result = f"Files in {project_path}:\n"
            for file in files:
                result += f"- {file['name']} ({file['type']})\n"
                if file['type'] == 'blob':
                    result += f"  Path: {file['path']}\n"
            
            return result

        @self.mcp.resource("gitlab://{owner}/{repo}/file/{path}")
        async def get_file_content(owner: str, repo: str, path: str) -> str:
            project_path = f"{owner}/{repo}"
            encoded_path = path.replace('/', '%2F')
            
            response = await self.client.get(
                f"{self.api_url}/projects/{project_path.replace('/', '%2F')}/repository/files/{encoded_path}/raw"
            )
            response.raise_for_status()
            
            return response.text

    def _setup_tools(self):
        @self.mcp.tool()
        async def search_code(
            query: str,
            owner: Optional[str] = None,
            repo: Optional[str] = None,
            scope: str = "blobs"
        ) -> Dict[str, Any]:
            params = {
                "search": query,
                "scope": scope
            }
            
            if owner and repo:
                project_path = f"{owner}/{repo}"
                project_id = await self._get_project_id(project_path)
                url = f"{self.api_url}/projects/{project_id}/search"
            else:
                url = f"{self.api_url}/search"
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            results = response.json()
            
            formatted_results = []
            for result in results[:20]:  # Limit results
                formatted_results.append({
                    "repository": result.get("project_id") or "Global",
                    "file": result.get("filename", result.get("path", "Unknown")),
                    "line": result.get("startline", "N/A"),
                    "preview": result.get("data", "")[:100]
                })
            
            return {"results": formatted_results}

        @self.mcp.tool()
        async def get_file_content(
            owner: str,
            repo: str,
            path: str,
            ref: str = "main"
        ) -> Dict[str, Any]:
            project_path = f"{owner}/{repo}"
            encoded_path = path.replace('/', '%2F')
            
            response = await self.client.get(
                f"{self.api_url}/projects/{project_path.replace('/', '%2F')}/repository/files/{encoded_path}",
                params={"ref": ref}
            )
            response.raise_for_status()
            file_data = response.json()
            
            import base64
            content = base64.b64decode(file_data["content"]).decode("utf-8")
            
            return {
                "content": content,
                "size": file_data["size"],
                "encoding": file_data["encoding"],
                "file_name": file_data["file_name"],
                "file_path": file_data["file_path"]
            }

        @self.mcp.tool()
        async def list_commits(
            owner: str,
            repo: str,
            branch: str = "main",
            limit: int = 10
        ) -> Dict[str, Any]:
            project_path = f"{owner}/{repo}"
            
            response = await self.client.get(
                f"{self.api_url}/projects/{project_path.replace('/', '%2F')}/repository/commits",
                params={"ref_name": branch, "per_page": limit}
            )
            response.raise_for_status()
            commits = response.json()
            
            formatted_commits = []
            for commit in commits:
                formatted_commits.append({
                    "id": commit["id"],
                    "message": commit["message"],
                    "author": commit["author_name"],
                    "date": commit["created_at"],
                    "url": commit["web_url"]
                })
            
            return {"commits": formatted_commits}

    async def _get_project_id(self, project_path: str) -> str:
        response = await self.client.get(
            f"{self.api_url}/projects/{project_path.replace('/', '%2F')}"
        )
        response.raise_for_status()
        return str(response.json()["id"])

    async def run_server(self):
        await self.mcp.run(transport="stdio")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()


async def main():
    server = GitLabMCPServer()
    await server.run_server()


if __name__ == "__main__":
    asyncio.run(main())