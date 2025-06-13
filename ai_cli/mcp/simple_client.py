import asyncio
from typing import Dict, List, Any, Optional
import httpx


class SimpleGitHubClient:
    """Simplified GitHub client that works without MCP dependencies."""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            },
            timeout=30.0
        )

    async def search_code(
        self,
        query: str,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search code in GitHub repositories."""
        search_query = query
        
        if owner and repo:
            search_query += f" repo:{owner}/{repo}"
        elif owner:
            search_query += f" user:{owner}"
        
        if language:
            search_query += f" language:{language}"
        
        try:
            url = f"{self.base_url}/search/code"
            params = {"q": search_query, "per_page": 20}
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            results = response.json()
            
            formatted_results = []
            for item in results.get("items", []):
                formatted_results.append({
                    "repository": item["repository"]["full_name"],
                    "file": item["name"],
                    "path": item["path"],
                    "url": item["html_url"],
                    "score": item["score"],
                    "owner": item["repository"]["owner"]["login"],
                    "repo_name": item["repository"]["name"]
                })
            
            return {
                "results": formatted_results, 
                "total_count": results.get("total_count", 0)
            }
        except Exception as e:
            return {"error": str(e), "results": []}

    async def get_user_repos(self) -> List[Dict[str, Any]]:
        """Get user repositories including private ones."""
        try:
            # Get all repositories including private ones with pagination
            all_repos = []
            page = 1
            per_page = 100
            
            while True:
                params = {
                    "type": "all",  # Include public, private, and organization repos
                    "sort": "updated",
                    "per_page": per_page,
                    "page": page
                }
                
                response = await self.client.get(f"{self.base_url}/user/repos", params=params)
                response.raise_for_status()
                repos = response.json()
                
                if not repos:  # No more repositories
                    break
                
                all_repos.extend(repos)
                
                if len(repos) < per_page:  # Last page
                    break
                    
                page += 1
                
                # Safety limit to avoid infinite loops
                if page > 10:  # Max 1000 repos
                    break
            
            formatted_repos = []
            for repo in all_repos:
                formatted_repos.append({
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo.get("description", ""),
                    "language": repo.get("language", ""),
                    "stars": repo["stargazers_count"],
                    "private": repo["private"],
                    "url": repo["html_url"]
                })
            
            return formatted_repos
        except Exception as e:
            return [{"error": str(e)}]

    async def validate_connection(self) -> bool:
        """Test if the GitHub token works."""
        try:
            response = await self.client.get(f"{self.base_url}/user")
            response.raise_for_status()
            return True
        except Exception:
            return False

    async def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str = "main"
    ) -> Dict[str, Any]:
        """Get file content from GitHub repository."""
        try:
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
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()



class SimpleGitLabClient:
    """Simplified GitLab client that works without MCP dependencies."""
    
    def __init__(self, token: str, base_url: str = "https://gitlab.com"):
        self.token = token
        self.base_url = base_url
        self.api_url = f"{self.base_url}/api/v4"
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=30.0
        )

    async def search_code(
        self,
        query: str,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        scope: str = "blobs"
    ) -> Dict[str, Any]:
        """Search code in GitLab repositories."""
        params = {
            "search": query,
            "scope": scope
        }
        
        try:
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
                    "preview": result.get("data", "")[:100],
                    "path": result.get("path", "Unknown")
                })
            
            return {"results": formatted_results}
        except Exception as e:
            return {"error": str(e), "results": []}

    async def _get_project_id(self, project_path: str) -> str:
        """Get project ID from project path."""
        try:
            response = await self.client.get(
                f"{self.api_url}/projects/{project_path.replace('/', '%2F')}"
            )
            response.raise_for_status()
            return str(response.json()["id"])
        except:
            return "unknown"

    async def validate_connection(self) -> bool:
        """Test if the GitLab token works."""
        try:
            response = await self.client.get(f"{self.api_url}/user")
            return response.status_code == 200
        except:
            return False

    async def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str = "main"
    ) -> Dict[str, Any]:
        """Get file content from GitLab repository."""
        try:
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
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()