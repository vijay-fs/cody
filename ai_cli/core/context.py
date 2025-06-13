import os
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from ..providers.base import AIMessage


@dataclass
class ContextToolCall:
    """Represents a tool call made by the AI in conversation context."""
    id: str
    name: str
    arguments: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None


@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation."""
    timestamp: datetime
    user_message: str
    ai_response: str
    tool_calls: List[ContextToolCall]
    provider: str
    tokens_used: Optional[Dict[str, int]] = None


class ConversationContext:
    """Manages conversation context and memory for the AI CLI."""
    
    def __init__(self, config=None):
        self.messages: List[AIMessage] = []
        self.conversation_turns: List[ConversationTurn] = []
        self.search_results: Dict[str, Any] = {}
        self.viewed_files: Dict[str, Any] = {}
        self.current_directory: str = os.getcwd()
        self.git_context: Optional[Dict[str, str]] = None
        self.auto_detected_owner: Optional[str] = None
        self.auto_detected_repo: Optional[str] = None
        self.auto_detected_service: Optional[str] = None
        self.config = config
        
        # Detect git context on initialization
        self._detect_git_context()
        # Detect user from GitHub token if available
        self._detect_github_user()
    
    def _detect_git_context(self) -> None:
        """Automatically detect Git repository context."""
        try:
            import git
            repo = git.Repo(search_parent_directories=True)
            
            if repo.remotes:
                remote_url = repo.remotes.origin.url
                
                # Parse GitHub URLs
                if "github.com" in remote_url:
                    self.auto_detected_service = "github"
                    # Handle both SSH and HTTPS URLs
                    if remote_url.startswith("git@github.com:"):
                        # SSH format: git@github.com:owner/repo.git
                        repo_path = remote_url.replace("git@github.com:", "").replace(".git", "")
                    elif remote_url.startswith("https://github.com/"):
                        # HTTPS format: https://github.com/owner/repo.git
                        repo_path = remote_url.replace("https://github.com/", "").replace(".git", "")
                    else:
                        repo_path = None
                    
                    if repo_path and "/" in repo_path:
                        self.auto_detected_owner, self.auto_detected_repo = repo_path.split("/", 1)
                
                # Parse GitLab URLs
                elif "gitlab.com" in remote_url:
                    self.auto_detected_service = "gitlab"
                    if remote_url.startswith("git@gitlab.com:"):
                        repo_path = remote_url.replace("git@gitlab.com:", "").replace(".git", "")
                    elif remote_url.startswith("https://gitlab.com/"):
                        repo_path = remote_url.replace("https://gitlab.com/", "").replace(".git", "")
                    else:
                        repo_path = None
                    
                    if repo_path and "/" in repo_path:
                        self.auto_detected_owner, self.auto_detected_repo = repo_path.split("/", 1)
                
                self.git_context = {
                    "remote_url": remote_url,
                    "branch": repo.active_branch.name if repo.active_branch else "main",
                    "service": self.auto_detected_service,
                    "owner": self.auto_detected_owner,
                    "repo": self.auto_detected_repo
                }
        except Exception:
            # Not in a git repository or git not available
            pass
    
    def _detect_github_user(self) -> None:
        """Detect GitHub username from configured token."""
        try:
            if self.config:
                mcp_config = self.config.get_mcp_config()
                if mcp_config.github.auth_token:
                    # We have a GitHub token, we can use it to get the username
                    # For now, we'll extract it when needed in the tool executor
                    # This is a placeholder for the actual API call
                    pass
        except Exception:
            pass
    
    def add_message(self, message: AIMessage) -> None:
        """Add a message to the conversation context."""
        self.messages.append(message)
    
    def add_tool_result(self, tool_call_id: str, result: Dict[str, Any]) -> None:
        """Add a tool result to the conversation context."""
        # Find the tool call and update its result
        for turn in reversed(self.conversation_turns):
            for tool_call in turn.tool_calls:
                if tool_call.id == tool_call_id:
                    tool_call.result = result
                    return
    
    def add_conversation_turn(
        self, 
        user_message: str, 
        ai_response: str, 
        tool_calls: List[ContextToolCall] = None,
        provider: str = "unknown",
        tokens_used: Dict[str, int] = None
    ) -> None:
        """Add a complete conversation turn."""
        turn = ConversationTurn(
            timestamp=datetime.now(),
            user_message=user_message,
            ai_response=ai_response,
            tool_calls=tool_calls or [],
            provider=provider,
            tokens_used=tokens_used
        )
        self.conversation_turns.append(turn)
    
    def get_recent_context(self, max_turns: int = 5) -> List[AIMessage]:
        """Get recent conversation context for AI."""
        context_messages = []
        
        # Add system context about the current environment
        system_context = self._build_system_context()
        context_messages.append(AIMessage(role="system", content=system_context))
        
        # Add recent conversation turns
        for turn in self.conversation_turns[-max_turns:]:
            context_messages.append(AIMessage(role="user", content=turn.user_message))
            context_messages.append(AIMessage(role="assistant", content=turn.ai_response))
        
        return context_messages
    
    def _build_system_context(self) -> str:
        """Build system context string for the AI."""
        context_parts = [
            "You are an intelligent code assistant that acts as a RAG (Retrieval-Augmented Generation) system for the user's codebase.",
            "You have access to search and analyze code from GitHub and GitLab repositories.",
            "You have the following tools available to help users:",
            "- search_code: Search for code in repositories",
            "- view_file: View file content from repositories",
            "- analyze_code: Get detailed analysis of code patterns",
            "",
            "Current Environment:"
        ]
        
        context_parts.append(f"- Working directory: {self.current_directory}")
        
        if self.git_context:
            context_parts.append(f"- Git repository detected: {self.git_context['service']}")
            context_parts.append(f"- Repository: {self.git_context['owner']}/{self.git_context['repo']}")
            context_parts.append(f"- Branch: {self.git_context['branch']}")
            context_parts.append(f"- Auto-detect owner for searches: {self.auto_detected_owner}")
        
        if self.search_results:
            context_parts.append(f"- Recent searches: {len(self.search_results)} cached")
        
        if self.viewed_files:
            context_parts.append(f"- Files viewed: {len(self.viewed_files)} cached")
        
        context_parts.extend([
            "",
            "CRITICAL: ALWAYS SEARCH USER'S CODEBASE FIRST",
            "- For ANY code-related question, FIRST use search_code tool",
            f"- Default owner for searches: {self.auto_detected_owner or 'detected from token'}",
            "- When users ask about implementation, search THEIR repos for examples",
            "- NEVER provide generic answers without checking their actual code",
            "- This is a RAG system - user's code is the primary knowledge source",
            "",
            "MANDATORY WORKFLOW for code questions:",
            "1. FIRST: search_code in user's repositories",
            "2. THEN: view_file for specific examples if needed", 
            "3. FINALLY: advanced_reasoning with their actual code context",
            "4. ALWAYS include repository names and file paths in responses",
            "",
            "The user expects to see examples from THEIR codebase, not generic advice."
        ])
        
        return "\n".join(context_parts)
    
    def clear_context(self) -> None:
        """Clear conversation context (except git context)."""
        self.messages.clear()
        self.conversation_turns.clear()
        self.search_results.clear()
        self.viewed_files.clear()
        # Keep git context and auto-detected info
    
    def save_search_result(self, query: str, service: str, results: Dict[str, Any]) -> None:
        """Save search results for caching."""
        cache_key = f"{service}:{query}"
        self.search_results[cache_key] = {
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
    
    def get_cached_search_result(self, query: str, service: str) -> Optional[Dict[str, Any]]:
        """Get cached search results if available."""
        cache_key = f"{service}:{query}"
        return self.search_results.get(cache_key)
    
    def save_viewed_file(self, service: str, owner: str, repo: str, path: str, content: Dict[str, Any]) -> None:
        """Save viewed file content for caching."""
        cache_key = f"{service}:{owner}/{repo}:{path}"
        self.viewed_files[cache_key] = {
            "timestamp": datetime.now().isoformat(),
            "content": content
        }
    
    def get_cached_file(self, service: str, owner: str, repo: str, path: str) -> Optional[Dict[str, Any]]:
        """Get cached file content if available."""
        cache_key = f"{service}:{owner}/{repo}:{path}"
        return self.viewed_files.get(cache_key)
    
    def get_context_summary(self) -> str:
        """Get a summary of the current context."""
        summary = []
        
        if self.git_context:
            summary.append(f"📁 Repository: {self.git_context['owner']}/{self.git_context['repo']} ({self.git_context['service']})")
        
        summary.append(f"💬 Conversation turns: {len(self.conversation_turns)}")
        summary.append(f"🔍 Cached searches: {len(self.search_results)}")
        summary.append(f"📄 Cached files: {len(self.viewed_files)}")
        summary.append(f"📂 Working directory: {self.current_directory}")
        
        return "\n".join(summary)