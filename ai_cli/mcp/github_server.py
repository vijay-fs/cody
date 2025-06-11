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


class GitHubMCPServer:
    def __init__(self):
        if not MCP_AVAILABLE:
            raise ImportError("MCP not available. Install with: pip install mcp fastmcp")
            
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = os.getenv("GITHUB_BASE_URL", "https://api.github.com")
        
        if not self.token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            },
            timeout=30.0
        )
        
        self.mcp = FastMCP("GitHub MCP Server")
        self._setup_resources()
        self._setup_tools()

    def _setup_resources(self):
        @self.mcp.resource("github://user/repos")
        async def list_user_repositories() -> str:
            response = await self.client.get(f"{self.base_url}/user/repos")
            response.raise_for_status()
            repos = response.json()
            
            result = "Your GitHub Repositories:\n"
            for repo in repos[:10]:  # Limit to first 10
                result += f"- {repo['name']} ({repo['full_name']})\n"
                result += f"  URL: {repo['html_url']}\n"
                result += f"  Description: {repo.get('description', 'No description')}\n"
                result += f"  Language: {repo.get('language', 'Not specified')}\n\n"
            
            return result

        @self.mcp.resource("github://{owner}/{repo}/contents")
        async def list_repository_contents(owner: str, repo: str) -> str:
            response = await self.client.get(
                f"{self.base_url}/repos/{owner}/{repo}/contents"
            )
            response.raise_for_status()
            contents = response.json()
            
            result = f"Contents of {owner}/{repo}:\n"
            for item in contents:
                result += f"- {item['name']} ({item['type']})\n"
                if item['type'] == 'file':
                    result += f"  Size: {item['size']} bytes\n"
                result += f"  Path: {item['path']}\n"
            
            return result

        @self.mcp.resource("github://{owner}/{repo}/file/{path}")
        async def get_file_content(owner: str, repo: str, path: str) -> str:
            response = await self.client.get(
                f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
            )
            response.raise_for_status()
            file_data = response.json()
            
            if file_data.get("encoding") == "base64":
                import base64
                content = base64.b64decode(file_data["content"]).decode("utf-8")
                return content
            else:
                return file_data.get("content", "")

    def _setup_tools(self):
        @self.mcp.tool()
        async def search_code(
            query: str,
            owner: Optional[str] = None,
            repo: Optional[str] = None,
            language: Optional[str] = None
        ) -> Dict[str, Any]:
            search_query = query
            
            if owner and repo:
                search_query += f" repo:{owner}/{repo}"
            elif owner:
                search_query += f" user:{owner}"
            
            if language:
                search_query += f" language:{language}"
            
            response = await self.client.get(
                f"{self.base_url}/search/code",
                params={"q": search_query, "per_page": 20}
            )
            response.raise_for_status()
            results = response.json()
            
            formatted_results = []
            for item in results.get("items", []):
                formatted_results.append({
                    "repository": item["repository"]["full_name"],
                    "file": item["name"],
                    "path": item["path"],
                    "url": item["html_url"],
                    "score": item["score"]
                })
            
            return {"results": formatted_results, "total_count": results.get("total_count", 0)}

        @self.mcp.tool()
        async def get_file_content(
            owner: str,
            repo: str,
            path: str,
            ref: str = "main"
        ) -> Dict[str, Any]:
            response = await self.client.get(
                f"{self.base_url}/repos/{owner}/{repo}/contents/{path}",
                params={"ref": ref}
            )
            response.raise_for_status()
            file_data = response.json()
            
            content = ""
            if file_data.get("encoding") == "base64":
                import base64
                content = base64.b64decode(file_data["content"]).decode("utf-8")
            else:
                content = file_data.get("content", "")
            
            return {
                "content": content,
                "size": file_data["size"],
                "encoding": file_data["encoding"],
                "name": file_data["name"],
                "path": file_data["path"],
                "sha": file_data["sha"],
                "url": file_data["html_url"]
            }

        @self.mcp.tool()
        async def list_commits(
            owner: str,
            repo: str,
            branch: str = "main",
            limit: int = 10
        ) -> Dict[str, Any]:
            response = await self.client.get(
                f"{self.base_url}/repos/{owner}/{repo}/commits",
                params={"sha": branch, "per_page": limit}
            )
            response.raise_for_status()
            commits = response.json()
            
            formatted_commits = []
            for commit in commits:
                formatted_commits.append({
                    "sha": commit["sha"],
                    "message": commit["commit"]["message"],
                    "author": commit["commit"]["author"]["name"],
                    "date": commit["commit"]["author"]["date"],
                    "url": commit["html_url"]
                })
            
            return {"commits": formatted_commits}

        @self.mcp.tool()
        async def search_repositories(
            query: str,
            sort: str = "stars",
            order: str = "desc",
            limit: int = 10
        ) -> Dict[str, Any]:
            response = await self.client.get(
                f"{self.base_url}/search/repositories",
                params={
                    "q": query,
                    "sort": sort,
                    "order": order,
                    "per_page": limit
                }
            )
            response.raise_for_status()
            results = response.json()
            
            formatted_repos = []
            for repo in results.get("items", []):
                formatted_repos.append({
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo.get("description", ""),
                    "language": repo.get("language", ""),
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "url": repo["html_url"]
                })
            
            return {"repositories": formatted_repos, "total_count": results.get("total_count", 0)}

        @self.mcp.tool()
        async def get_repository_info(owner: str, repo: str) -> Dict[str, Any]:
            response = await self.client.get(f"{self.base_url}/repos/{owner}/{repo}")
            response.raise_for_status()
            repo_data = response.json()
            
            return {
                "id": repo_data["id"],
                "name": repo_data["name"],
                "full_name": repo_data["full_name"],
                "description": repo_data.get("description", ""),
                "language": repo_data.get("language", ""),
                "stars": repo_data["stargazers_count"],
                "forks": repo_data["forks_count"],
                "issues": repo_data["open_issues_count"],
                "created_at": repo_data["created_at"],
                "updated_at": repo_data["updated_at"],
                "url": repo_data["html_url"],
                "clone_url": repo_data["clone_url"],
                "default_branch": repo_data["default_branch"]
            }

    async def run_server(self):
        await self.mcp.run(transport="stdio")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()


async def main():
    server = GitHubMCPServer()
    await server.run_server()


if __name__ == "__main__":
    asyncio.run(main())