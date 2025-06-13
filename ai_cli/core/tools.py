from typing import Dict, List, Any, Optional
import json
from dataclasses import dataclass

from ..mcp.simple_client import SimpleGitHubClient, SimpleGitLabClient
from ..core.config import AICliConfig
from .context import ConversationContext
from .nlp_search import SemanticSearchOptimizer, enhance_search_with_nlp
from .reasoning import AdvancedReasoningEngine


@dataclass
class ToolDefinition:
    """Definition of a tool that can be called by the AI."""
    name: str
    description: str
    parameters: Dict[str, Any]


# Tool definitions for AI
AVAILABLE_TOOLS = [
    ToolDefinition(
        name="search_code",
        description="MANDATORY FIRST STEP: Search for code examples in the user's own repositories. ALWAYS use this FIRST for ANY code-related question before giving answers. Required for: 'how to implement', 'show me examples', 'find patterns', websockets, authentication, APIs, architecture questions, etc. This is a RAG system - user's code is the primary knowledge source.",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string", 
                    "description": "Search query - specific terms like 'nextjs app routing', 'React authentication', 'S3 integration', etc."
                },
                "service": {
                    "type": "string", 
                    "enum": ["github", "gitlab"],
                    "description": "Service to search - use 'github' by default"
                },
                "owner": {
                    "type": "string", 
                    "description": "Repository owner - will be auto-filled with user's username to search their repos"
                },
                "repo": {
                    "type": "string", 
                    "description": "Specific repository name (optional) - leave empty to search all user repos"
                }
            },
            "required": ["query", "service"]
        }
    ),
    ToolDefinition(
        name="view_file",
        description="View the complete content of a specific file from a repository. Use this when you need to see the full implementation of a file found in search results.",
        parameters={
            "type": "object",
            "properties": {
                "service": {
                    "type": "string", 
                    "enum": ["github", "gitlab"],
                    "description": "Service where the file is located"
                },
                "owner": {
                    "type": "string",
                    "description": "Repository owner"
                },
                "repo": {
                    "type": "string",
                    "description": "Repository name"
                },
                "path": {
                    "type": "string",
                    "description": "Full path to the file in the repository"
                }
            },
            "required": ["service", "owner", "repo", "path"]
        }
    ),
    ToolDefinition(
        name="analyze_code_context",
        description="Analyze code context from search results or viewed files to answer user questions. Use this after gathering code to provide detailed analysis.",
        parameters={
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The user's original question to answer"
                },
                "context_sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of code sources being analyzed"
                }
            },
            "required": ["question", "context_sources"]
        }
    ),
    ToolDefinition(
        name="advanced_reasoning",
        description="Apply advanced reasoning for complex technical questions requiring deep analysis, system design, architecture decisions, or multi-step problem solving. Use for expert-level queries.",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The complex technical question or problem to analyze"
                },
                "domain": {
                    "type": "string",
                    "description": "Technical domain (e.g., 'architecture', 'security', 'performance', 'websocket', 'authentication')"
                },
                "code_context": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Available code examples and context for reasoning"
                }
            },
            "required": ["query", "domain"]
        }
    )
]


class ToolExecutor:
    """Executes tools called by the AI."""
    
    def __init__(self, config: AICliConfig, context: ConversationContext):
        self.config = config
        self.context = context
        self.nlp_optimizer = SemanticSearchOptimizer()
        self.reasoning_engine = AdvancedReasoningEngine()
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with the given arguments."""
        try:
            if tool_name == "search_code":
                return await self._search_code(**arguments)
            elif tool_name == "view_file":
                return await self._view_file(**arguments)
            elif tool_name == "analyze_code_context":
                return await self._analyze_code_context(**arguments)
            elif tool_name == "advanced_reasoning":
                return await self._advanced_reasoning(**arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    async def _search_code(
        self, 
        query: str, 
        service: str, 
        owner: str = None, 
        repo: str = None
    ) -> Dict[str, Any]:
        """Search for code in repositories with NLP optimization."""
        
        # ALWAYS prioritize user's own repositories for code searches
        # If no owner specified, get the authenticated user's username
        if not owner:
            if self.context.auto_detected_owner:
                owner = self.context.auto_detected_owner
            else:
                # Get authenticated user from GitHub API
                owner = await self._get_authenticated_user(service)
                if owner:
                    self.context.auto_detected_owner = owner
            
        # If no repo specified but we have auto-detected repo, use it for specific searches
        if not repo and self.context.auto_detected_repo:
            # For general queries, search across all user repos, not just current one
            if not any(keyword in query.lower() for keyword in ['current', 'this project', 'this repo']):
                # Search across all user's repositories
                pass  # Leave repo as None to search all user repos
            else:
                repo = self.context.auto_detected_repo
        
        # Check cache first
        cached_result = self.context.get_cached_search_result(query, service)
        if cached_result:
            return {
                "cached": True,
                "results": cached_result["results"],
                "message": f"Using cached results for '{query}' on {service}"
            }
        
        # Use NLP optimization to enhance the search
        nlp_enhancement = enhance_search_with_nlp(query, self.nlp_optimizer)
        optimized_queries = nlp_enhancement["optimized_queries"]
        intent = nlp_enhancement["intent"]
        
        # Try multiple search strategies
        all_results = []
        search_attempts = []
        
        # Get MCP configuration
        mcp_config = self.config.get_mcp_config()
        
        # Execute enhanced searches
        
        if service == "github":
            token = mcp_config.github.auth_token
            if not token:
                return {"error": "GitHub not configured. Use setup commands first."}
            
            client = SimpleGitHubClient(token)
            try:
                # Try multiple optimized search queries
                for i, optimized_query in enumerate(optimized_queries[:4]):  # Limit to 4 attempts
                    search_attempts.append(optimized_query)
                    
                    results_data = await client.search_code(optimized_query, owner, repo)
                    
                    if "error" not in results_data and results_data.get("results"):
                        all_results.extend(results_data.get("results", []))
                        
                        # If we found good results early, we can stop
                        if len(all_results) >= 10:
                            break
                
                # If no results with optimized queries, try original
                if not all_results:
                    results_data = await client.search_code(query, owner, repo)
                    if "error" not in results_data:
                        all_results.extend(results_data.get("results", []))
                
                # Remove duplicates based on repository + path
                seen = set()
                unique_results = []
                for result in all_results:
                    key = f"{result.get('repository', '')}/{result.get('path', '')}"
                    if key not in seen:
                        seen.add(key)
                        unique_results.append(result)
                
                # Sort by relevance (score if available)
                unique_results.sort(key=lambda x: x.get('score', 0), reverse=True)
                
                # Cache the results
                cache_data = {
                    "results": unique_results[:15],
                    "total_count": len(unique_results)
                }
                self.context.save_search_result(query, service, cache_data)
                
                return {
                    "service": service,
                    "query": query,
                    "original_query": query,
                    "optimized_queries": optimized_queries,
                    "search_attempts": search_attempts,
                    "intent": intent,
                    "owner": owner,
                    "repo": repo,
                    "total_count": len(unique_results),
                    "results": unique_results[:10],  # Return top 10
                    "message": f"Found {len(unique_results)} results using NLP-enhanced search for '{query}' on GitHub"
                }
            finally:
                await client.close()
        
        elif service == "gitlab":
            token = mcp_config.gitlab.auth_token
            if not token:
                return {"error": "GitLab not configured. Use setup commands first."}
            
            client = SimpleGitLabClient(token, mcp_config.gitlab.base_url)
            try:
                results_data = await client.search_code(query, owner, repo)
                
                if "error" in results_data:
                    return {"error": results_data["error"]}
                
                # Cache the results
                self.context.save_search_result(query, service, results_data)
                
                return {
                    "service": service,
                    "query": query,
                    "owner": owner,
                    "repo": repo,
                    "results": results_data.get("results", [])[:10],  # Limit to top 10
                    "message": f"Found {len(results_data.get('results', []))} results for '{query}' on GitLab"
                }
            finally:
                await client.close()
        
        return {"error": f"Unsupported service: {service}"}
    
    async def _view_file(
        self, 
        service: str, 
        owner: str, 
        repo: str, 
        path: str
    ) -> Dict[str, Any]:
        """View file content from a repository."""
        
        # Check cache first
        cached_file = self.context.get_cached_file(service, owner, repo, path)
        if cached_file:
            return {
                "cached": True,
                "content": cached_file["content"],
                "message": f"Using cached content for {owner}/{repo}/{path}"
            }
        
        # Get MCP configuration
        mcp_config = self.config.get_mcp_config()
        
        if service == "github":
            token = mcp_config.github.auth_token
            if not token:
                return {"error": "GitHub not configured. Use setup commands first."}
            
            client = SimpleGitHubClient(token)
            try:
                file_data = await client.get_file_content(owner, repo, path)
                
                if "error" in file_data:
                    return {"error": file_data["error"]}
                
                # Cache the file content
                self.context.save_viewed_file(service, owner, repo, path, file_data)
                
                return {
                    "service": service,
                    "owner": owner,
                    "repo": repo,
                    "path": path,
                    "file_info": {
                        "name": file_data.get("name", "Unknown"),
                        "size": file_data.get("size", 0),
                        "url": file_data.get("url", "")
                    },
                    "content": file_data.get("content", ""),
                    "message": f"Retrieved {file_data.get('size', 0)} bytes from {owner}/{repo}/{path}"
                }
            finally:
                await client.close()
        
        elif service == "gitlab":
            token = mcp_config.gitlab.auth_token
            if not token:
                return {"error": "GitLab not configured. Use setup commands first."}
            
            client = SimpleGitLabClient(token, mcp_config.gitlab.base_url)
            try:
                file_data = await client.get_file_content(owner, repo, path)
                
                if "error" in file_data:
                    return {"error": file_data["error"]}
                
                # Cache the file content
                self.context.save_viewed_file(service, owner, repo, path, file_data)
                
                return {
                    "service": service,
                    "owner": owner,
                    "repo": repo,
                    "path": path,
                    "file_info": {
                        "name": file_data.get("file_name", "Unknown"),
                        "size": file_data.get("size", 0)
                    },
                    "content": file_data.get("content", ""),
                    "message": f"Retrieved {file_data.get('size', 0)} bytes from {owner}/{repo}/{path}"
                }
            finally:
                await client.close()
        
        return {"error": f"Unsupported service: {service}"}
    
    async def _analyze_code_context(
        self, 
        question: str, 
        context_sources: List[str]
    ) -> Dict[str, Any]:
        """Analyze code context to answer user questions."""
        
        # This is a meta-tool that helps structure the analysis
        # The actual analysis will be done by the AI with the gathered context
        
        return {
            "question": question,
            "context_sources": context_sources,
            "analysis_ready": True,
            "message": f"Ready to analyze {len(context_sources)} code sources to answer: '{question}'"
        }
    
    async def _get_authenticated_user(self, service: str) -> Optional[str]:
        """Get the authenticated user's username from the API."""
        try:
            mcp_config = self.config.get_mcp_config()
            
            if service == "github":
                token = mcp_config.github.auth_token
                if not token:
                    return None
                
                from ..mcp.simple_client import SimpleGitHubClient
                client = SimpleGitHubClient(token)
                try:
                    # Get authenticated user info
                    import httpx
                    response = await client.client.get(f"{client.base_url}/user")
                    response.raise_for_status()
                    user_data = response.json()
                    return user_data.get("login")
                finally:
                    await client.close()
            
            elif service == "gitlab":
                token = mcp_config.gitlab.auth_token
                if not token:
                    return None
                
                from ..mcp.simple_client import SimpleGitLabClient
                client = SimpleGitLabClient(token, mcp_config.gitlab.base_url)
                try:
                    # Get authenticated user info
                    import httpx
                    response = await client.client.get(f"{client.base_url}/user")
                    response.raise_for_status()
                    user_data = response.json()
                    return user_data.get("username")
                finally:
                    await client.close()
                    
        except Exception:
            pass
        
        return None
    
    async def _advanced_reasoning(
        self,
        query: str,
        domain: str,
        code_context: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Apply advanced reasoning to complex technical questions."""
        
        try:
            # Get current provider for model-specific optimization
            current_provider = self.config.default_provider
            current_model = self.config.providers.get(current_provider, {}).get("model", "o3-mini")
            
            # Enhance query with reasoning capabilities
            reasoning_enhancement = self.reasoning_engine.enhance_query_for_reasoning(
                original_query=query,
                code_context=code_context or [],
                domain=domain,
                model=current_model
            )
            
            context = reasoning_enhancement["reasoning_context"]
            enhanced_prompt = reasoning_enhancement["enhanced_prompt"]
            recommendations = reasoning_enhancement["recommendations"]
            
            return {
                "reasoning_mode": context.reasoning_mode.value,
                "complexity_level": context.complexity.value,
                "domain": domain,
                "enhanced_prompt": enhanced_prompt["prompt"],
                "reasoning_template": enhanced_prompt["reasoning_mode"],
                "model_optimized": enhanced_prompt["model_optimized"],
                "supports_reasoning": enhanced_prompt["supports_reasoning"],
                "recommendations": recommendations,
                "context_analysis": {
                    "code_examples": len(code_context or []),
                    "constraints": context.constraints,
                    "user_intent": context.user_intent
                },
                "estimated_tokens": recommendations["estimated_tokens"],
                "message": f"Applied {context.reasoning_mode.value} reasoning for {context.complexity.value} complexity {domain} question"
            }
            
        except Exception as e:
            return {
                "error": f"Advanced reasoning failed: {str(e)}",
                "fallback_mode": "standard_analysis",
                "message": "Falling back to standard analysis mode"
            }


def get_tool_definitions_for_ai() -> List[Dict[str, Any]]:
    """Get tool definitions in the format expected by AI providers."""
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
        }
        for tool in AVAILABLE_TOOLS
    ]


def should_use_auto_detected_context(query: str, context: ConversationContext) -> bool:
    """Determine if we should use auto-detected repository context for this query."""
    
    # Use auto-detected context if:
    # 1. We have detected a repository
    # 2. The query doesn't specify a different owner/repo
    # 3. The query seems to be about code in general (not asking about a specific external project)
    
    if not context.auto_detected_owner or not context.auto_detected_repo:
        return False
    
    # Keywords that suggest the user wants to search their own repo
    own_repo_keywords = [
        "my code", "this project", "our project", "this repo", "current project",
        "how do we", "how does this", "in this codebase", "our implementation"
    ]
    
    # Keywords that suggest they want to search external repos
    external_repo_keywords = [
        "examples from", "how do other", "popular implementations", "best practices",
        "in react", "in vue", "in angular", "in next.js", "in express"
    ]
    
    query_lower = query.lower()
    
    # Strong indicators for own repo
    if any(keyword in query_lower for keyword in own_repo_keywords):
        return True
    
    # Strong indicators for external repos
    if any(keyword in query_lower for keyword in external_repo_keywords):
        return False
    
    # Default to using own repo context if available
    return True