import asyncio
import shlex
import os
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from ..core.config import AICliConfig
from ..providers.factory import ProviderFactory
from ..providers.base import AIMessage
from ..mcp.simple_client import SimpleGitHubClient, SimpleGitLabClient

console = Console()

class InteractiveCLI:
    def __init__(self):
        self.config = AICliConfig()
        self.config.load_config_file()
        self.running = True
        
    def show_welcome(self):
        """Show welcome message and available commands."""
        welcome_text = """
# 🤖 AI CLI Interactive Mode

**Available Commands:**
- `/help` - Show this help message
- `/setup` - Add API keys (OpenAI, Claude, etc.)
- `/mcp` - Configure MCP connections (GitLab, GitHub)
- `/search` - Search GitHub/GitLab repositories OR local codebase
- `/local` - Search and analyze local codebase with AI
- `/view` - View file content from search results
- `/analyze` - Analyze code with AI after searching
- `/providers` - Show AI provider status
- `/config` - Show current configuration
- `/exit` or `/quit` - Exit the application

**Chat with AI:**
- Just type your message and press Enter
- Use `--provider claude` to specify provider
- Use `--stream` for streaming responses

**Examples:**
- `Hello, how are you?`
- `Explain Python decorators --provider claude`
- `Write a function --stream`
- `/search github "authentication function"`
- `/search gitlab "bug fix" --owner myorg --repo backend`
- `/local "websocket architecture"` - Search your local codebase
- `/view github owner/repo path/to/file.py`
- `/analyze github "How does authentication work?" --query "login function"`
        """
        console.print(Panel(Markdown(welcome_text), title="Welcome to AI CLI", border_style="blue"))

    def show_help(self):
        """Show help information."""
        self.show_welcome()

    async def handle_setup_command(self, args: list):
        """Handle API key setup commands."""
        if not args:
            await self.show_setup_options()
            return
            
        subcommand = args[0].lower()
        
        if subcommand == "openai":
            await self.setup_openai()
        elif subcommand == "claude":
            await self.setup_claude()
        elif subcommand == "azure":
            await self.setup_azure_openai()
        elif subcommand == "all":
            await self.setup_all_providers()
        else:
            console.print("[red]Unknown setup option. Available: openai, claude, azure, all[/red]")

    async def show_setup_options(self):
        """Show setup options for API keys."""
        table = Table(title="AI Provider Setup")
        table.add_column("Provider", style="cyan")
        table.add_column("Command", style="yellow")
        table.add_column("Status", style="green")
        
        # Check current status
        providers_status = {}
        for provider_name in ["openai", "claude", "azure_openai"]:
            try:
                provider_config = self.config.get_provider_config(provider_name).model_dump()
                has_key = bool(provider_config.get("api_key"))
                providers_status[provider_name] = "✓ Configured" if has_key else "✗ Not configured"
            except:
                providers_status[provider_name] = "✗ Not configured"
        
        table.add_row("OpenAI", "/setup openai", providers_status.get("openai", "✗ Not configured"))
        table.add_row("Claude", "/setup claude", providers_status.get("claude", "✗ Not configured"))
        table.add_row("Azure OpenAI", "/setup azure", providers_status.get("azure_openai", "✗ Not configured"))
        table.add_row("All Providers", "/setup all", "Setup all at once")
        
        console.print(table)
        console.print("\n[dim]Example: /setup openai[/dim]")

    async def setup_openai(self):
        """Setup OpenAI API key."""
        console.print(Panel(
            "[bold blue]OpenAI Setup[/bold blue]\n\n"
            "1. Go to https://platform.openai.com/api-keys\n"
            "2. Sign in to your OpenAI account\n"
            "3. Click 'Create new secret key'\n"
            "4. Copy the key (starts with 'sk-proj-' or 'sk-')",
            title="OpenAI API Key Setup"
        ))
        
        api_key = Prompt.ask("Enter your OpenAI API key", password=True)
        
        if not api_key:
            console.print("[red]No API key provided, cancelling.[/red]")
            return
        
        if not api_key.startswith("sk-"):
            console.print("[yellow]Warning: OpenAI API keys usually start with 'sk-'[/yellow]")
            
        # Test the API key
        console.print("Testing OpenAI connection...")
        try:
            from ..providers.openai_provider import OpenAIProvider
            provider = OpenAIProvider({"api_key": api_key})
            
            async with provider:
                is_valid = await provider.validate_connection()
                if is_valid:
                    # Save to config
                    self.config.providers["openai"]["api_key"] = api_key
                    self.config.providers["openai"]["model"] = "gpt-4"
                    self.config.providers["openai"]["max_tokens"] = 4000
                    self.config.providers["openai"]["temperature"] = 0.7
                    self.config.save_config_file()
                    console.print("[green]✓ OpenAI API key saved successfully![/green]")
                    
                    # Test a quick message
                    test_confirm = Confirm.ask("Would you like to test with a quick message?")
                    if test_confirm:
                        await self.handle_chat_message("Hello! Just testing the connection.")
                else:
                    console.print("[red]✗ Invalid OpenAI API key or connection failed[/red]")
        except Exception as e:
            console.print(f"[red]Error testing OpenAI connection: {e}[/red]")

    async def setup_claude(self):
        """Setup Claude API key."""
        console.print(Panel(
            "[bold blue]Claude (Anthropic) Setup[/bold blue]\n\n"
            "1. Go to https://console.anthropic.com\n"
            "2. Sign in to your Anthropic account\n"
            "3. Go to API Keys section\n"
            "4. Create a new key (starts with 'sk-ant-')",
            title="Claude API Key Setup"
        ))
        
        api_key = Prompt.ask("Enter your Claude API key", password=True)
        
        if not api_key:
            console.print("[red]No API key provided, cancelling.[/red]")
            return
            
        if not api_key.startswith("sk-ant-"):
            console.print("[yellow]Warning: Claude API keys usually start with 'sk-ant-'[/yellow]")
            
        # Test the API key
        console.print("Testing Claude connection...")
        try:
            from ..providers.claude_provider import ClaudeProvider
            provider = ClaudeProvider({"api_key": api_key})
            
            async with provider:
                is_valid = await provider.validate_connection()
                if is_valid:
                    # Save to config
                    self.config.providers["claude"]["api_key"] = api_key
                    self.config.providers["claude"]["model"] = "claude-3-sonnet-20240229"
                    self.config.providers["claude"]["max_tokens"] = 4000
                    self.config.providers["claude"]["temperature"] = 0.7
                    self.config.save_config_file()
                    console.print("[green]✓ Claude API key saved successfully![/green]")
                else:
                    console.print("[red]✗ Invalid Claude API key or connection failed[/red]")
        except Exception as e:
            console.print(f"[red]Error testing Claude connection: {e}[/red]")

    async def setup_azure_openai(self):
        """Setup Azure OpenAI."""
        console.print(Panel(
            "[bold blue]Azure OpenAI Setup[/bold blue]\n\n"
            "1. Go to Azure Portal\n"
            "2. Create an Azure OpenAI resource\n"
            "3. Get the endpoint URL and API key\n"
            "4. Note your deployment name",
            title="Azure OpenAI Setup"
        ))
        
        endpoint = Prompt.ask("Enter your Azure OpenAI endpoint URL")
        api_key = Prompt.ask("Enter your Azure OpenAI API key", password=True)
        deployment_name = Prompt.ask("Enter your deployment name", default="gpt-4")
        
        if not endpoint or not api_key:
            console.print("[red]Endpoint and API key are required, cancelling.[/red]")
            return
            
        # Save to config
        self.config.providers["azure_openai"]["endpoint"] = endpoint
        self.config.providers["azure_openai"]["api_key"] = api_key
        self.config.providers["azure_openai"]["deployment_name"] = deployment_name
        self.config.providers["azure_openai"]["api_version"] = "2024-02-01"
        self.config.save_config_file()
        console.print("[green]✓ Azure OpenAI configuration saved![/green]")

    async def setup_all_providers(self):
        """Setup all AI providers."""
        console.print("[bold blue]Setting up all AI providers...[/bold blue]\n")
        
        setup_openai = Confirm.ask("Setup OpenAI?", default=True)
        if setup_openai:
            await self.setup_openai()
            
        setup_claude = Confirm.ask("Setup Claude?", default=False)
        if setup_claude:
            await self.setup_claude()
            
        setup_azure = Confirm.ask("Setup Azure OpenAI?", default=False)
        if setup_azure:
            await self.setup_azure_openai()
            
        console.print("\n[green]✓ Setup complete! Use /providers to check status.[/green]")

    async def handle_mcp_command(self, args: list):
        """Handle MCP configuration commands."""
        if not args:
            await self.show_mcp_status()
            return
            
        subcommand = args[0].lower()
        
        if subcommand == "status":
            await self.show_mcp_status()
        elif subcommand == "add":
            await self.add_mcp_service()
        elif subcommand == "remove":
            await self.remove_mcp_service()
        elif subcommand == "test":
            if len(args) > 1:
                await self.test_mcp_service(args[1])
            else:
                console.print("[red]Usage: /mcp test <service>[/red]")
        else:
            console.print("[red]Unknown MCP command. Available: status, add, remove, test[/red]")

    async def show_mcp_status(self):
        """Show current MCP service status."""
        mcp_config = self.config.get_mcp_config()
        
        table = Table(title="MCP Services Configuration")
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Token", style="yellow")
        table.add_column("URL", style="blue")
        
        # GitHub
        github_token = mcp_config.github.auth_token
        github_status = "✓ Configured" if github_token else "✗ Not configured"
        github_token_display = f"{github_token[:10]}..." if github_token else "Not set"
        table.add_row("GitHub", github_status, github_token_display, mcp_config.github.base_url)
        
        # GitLab
        gitlab_token = mcp_config.gitlab.auth_token
        gitlab_status = "✓ Configured" if gitlab_token else "✗ Not configured"
        gitlab_token_display = f"{gitlab_token[:10]}..." if gitlab_token else "Not set"
        table.add_row("GitLab", gitlab_status, gitlab_token_display, mcp_config.gitlab.base_url)
        
        console.print(table)
        
        console.print("\n[dim]Commands: /mcp add, /mcp test <service>, /mcp remove[/dim]")

    async def add_mcp_service(self):
        """Interactive MCP service addition."""
        service_choice = Prompt.ask(
            "Which service would you like to configure?",
            choices=["github", "gitlab"],
            default="github"
        )
        
        if service_choice == "github":
            await self.configure_github()
        elif service_choice == "gitlab":
            await self.configure_gitlab()

    async def configure_github(self):
        """Configure GitHub MCP service."""
        console.print(Panel(
            "[bold blue]GitHub Configuration[/bold blue]\n\n"
            "1. Go to GitHub → Settings → Developer settings → Personal access tokens\n"
            "2. Create a new token with 'repo' and 'read:org' scopes\n"
            "3. Copy the token (starts with 'ghp_' or 'github_pat_')",
            title="GitHub Setup Instructions"
        ))
        
        token = Prompt.ask("Enter your GitHub personal access token", password=True)
        
        if not token:
            console.print("[red]No token provided, cancelling.[/red]")
            return
            
        # Test the token
        console.print("Testing GitHub connection...")
        client = SimpleGitHubClient(token)
        try:
            is_valid = await client.validate_connection()
            if is_valid:
                # Save to config
                self.config.mcp["github"]["auth_token"] = token
                self.config.save_config_file()
                console.print("[green]✓ GitHub token saved successfully![/green]")
                
                # Show user info
                repos = await client.get_user_repos()
                if repos and not repos[0].get("error"):
                    console.print(f"Found {len(repos)} repositories in your account.")
            else:
                console.print("[red]✗ Invalid GitHub token or connection failed[/red]")
        except Exception as e:
            console.print(f"[red]Error testing GitHub connection: {e}[/red]")
        finally:
            await client.close()

    async def configure_gitlab(self):
        """Configure GitLab MCP service."""
        console.print(Panel(
            "[bold blue]GitLab Configuration[/bold blue]\n\n"
            "1. Go to GitLab → User Settings → Access Tokens\n"
            "2. Create a new token with 'api' and 'read_repository' scopes\n"
            "3. Copy the token (starts with 'glpat-')",
            title="GitLab Setup Instructions"
        ))
        
        base_url = Prompt.ask("GitLab URL", default="https://gitlab.com")
        token = Prompt.ask("Enter your GitLab personal access token", password=True)
        
        if not token:
            console.print("[red]No token provided, cancelling.[/red]")
            return
            
        # Test the token
        console.print("Testing GitLab connection...")
        client = SimpleGitLabClient(token, base_url)
        try:
            is_valid = await client.validate_connection()
            if is_valid:
                # Save to config
                self.config.mcp["gitlab"]["auth_token"] = token
                self.config.mcp["gitlab"]["base_url"] = base_url
                self.config.save_config_file()
                console.print("[green]✓ GitLab token saved successfully![/green]")
            else:
                console.print("[red]✗ Invalid GitLab token or connection failed[/red]")
        except Exception as e:
            console.print(f"[red]Error testing GitLab connection: {e}[/red]")
        finally:
            await client.close()

    async def test_mcp_service(self, service: str):
        """Test MCP service connection."""
        mcp_config = self.config.get_mcp_config()
        
        if service == "github":
            token = mcp_config.github.auth_token
            if not token:
                console.print("[red]GitHub not configured. Use /mcp add first.[/red]")
                return
                
            client = SimpleGitHubClient(token)
            try:
                console.print("Testing GitHub connection...")
                is_valid = await client.validate_connection()
                if is_valid:
                    console.print("[green]✓ GitHub connection successful[/green]")
                    repos = await client.get_user_repos()
                    console.print(f"Found {len(repos)} repositories")
                else:
                    console.print("[red]✗ GitHub connection failed[/red]")
            finally:
                await client.close()
                
        elif service == "gitlab":
            token = mcp_config.gitlab.auth_token
            if not token:
                console.print("[red]GitLab not configured. Use /mcp add first.[/red]")
                return
                
            client = SimpleGitLabClient(token, mcp_config.gitlab.base_url)
            try:
                console.print("Testing GitLab connection...")
                is_valid = await client.validate_connection()
                if is_valid:
                    console.print("[green]✓ GitLab connection successful[/green]")
                else:
                    console.print("[red]✗ GitLab connection failed[/red]")
            finally:
                await client.close()
        else:
            console.print(f"[red]Unknown service: {service}[/red]")

    async def remove_mcp_service(self):
        """Remove MCP service configuration."""
        service_choice = Prompt.ask(
            "Which service would you like to remove?",
            choices=["github", "gitlab"],
        )
        
        confirm = Confirm.ask(f"Are you sure you want to remove {service_choice} configuration?")
        if confirm:
            self.config.mcp[service_choice] = {}
            self.config.save_config_file()
            console.print(f"[green]✓ {service_choice} configuration removed[/green]")

    async def handle_search_command(self, args: list):
        """Handle search command for GitHub/GitLab repositories or local codebase."""
        if len(args) < 2:
            console.print("[red]Usage: /search <service> <query> [--owner <owner>] [--repo <repo>][/red]")
            console.print("[dim]Example: /search github \"authentication function\"[/dim]")
            console.print("[dim]Example: /search gitlab \"bug fix\" --owner myorg --repo backend[/dim]")
            console.print("[dim]Example: /search local \"websocket architecture\"[/dim]")
            return
            
        service = args[0].lower()
        if service not in ["github", "gitlab", "local"]:
            console.print("[red]Service must be 'github', 'gitlab', or 'local'[/red]")
            return
            
        # Handle local search
        if service == "local":
            await self.handle_local_command(args[1:])
            return
            
        # Parse query and options (shlex will have handled quotes properly)
        query = args[1]
        owner = None
        repo = None
        
        # Parse remaining options
        i = 2
        while i < len(args):
            if args[i] == "--owner" and i + 1 < len(args):
                owner = args[i + 1]
                i += 2
            elif args[i] == "--repo" and i + 1 < len(args):
                repo = args[i + 1]
                i += 2
            else:
                i += 1
        
        if not query.strip():
            console.print("[red]Query cannot be empty[/red]")
            return
        
        await self.search_code(service, query, owner, repo)

    async def search_code(self, service: str, query: str, owner: str = None, repo: str = None):
        """Search code in GitHub or GitLab repositories."""
        mcp_config = self.config.get_mcp_config()
        
        if service == "github":
            token = mcp_config.github.auth_token
            if not token:
                console.print("[red]GitHub not configured. Use /mcp add to set up GitHub first.[/red]")
                return
                
            client = SimpleGitHubClient(token)
            try:
                console.print(f"[blue]Searching GitHub for: {query}[/blue]")
                console.print(f"[dim]Query length: {len(query)}, Query repr: {repr(query)}[/dim]")
                if owner:
                    console.print(f"[dim]Owner: {owner}[/dim]")
                if repo:
                    console.print(f"[dim]Repository: {repo}[/dim]")
                    
                results_data = await client.search_code(query, owner, repo)
                
                if "error" in results_data:
                    console.print(f"[red]Search failed: {results_data['error']}[/red]")
                    return
                
                results = results_data.get("results", [])
                total_count = results_data.get("total_count", 0)
                
                if results:
                    table = Table(title=f"Search Results from GitHub (Total: {total_count})")
                    table.add_column("Repository", style="cyan")
                    table.add_column("File", style="yellow")
                    table.add_column("Path", style="green")
                    table.add_column("Score", style="white")
                    
                    for result in results[:10]:  # Limit to first 10 results
                        table.add_row(
                            result.get("repository", "N/A"),
                            result.get("file", "N/A"),
                            result.get("path", "N/A")[:50] + "..." if len(result.get("path", "")) > 50 else result.get("path", "N/A"),
                            str(result.get("score", "N/A"))
                        )
                    
                    console.print(table)
                    
                    # Show additional context
                    if total_count > 10:
                        console.print(f"[dim]Showing first 10 of {total_count} results[/dim]")
                        
                else:
                    console.print("[yellow]No results found for your search query[/yellow]")
                    
            except Exception as e:
                console.print(f"[red]Search error: {e}[/red]")
            finally:
                await client.close()
                
        elif service == "gitlab":
            token = mcp_config.gitlab.auth_token
            if not token:
                console.print("[red]GitLab not configured. Use /mcp add to set up GitLab first.[/red]")
                return
                
            client = SimpleGitLabClient(token, mcp_config.gitlab.base_url)
            try:
                console.print(f"[blue]Searching GitLab for: {query}[/blue]")
                if owner:
                    console.print(f"[dim]Owner: {owner}[/dim]")
                if repo:
                    console.print(f"[dim]Repository: {repo}[/dim]")
                    
                results_data = await client.search_code(query, owner, repo)
                
                if "error" in results_data:
                    console.print(f"[red]Search failed: {results_data['error']}[/red]")
                    return
                
                results = results_data.get("results", [])
                
                if results:
                    table = Table(title=f"Search Results from GitLab")
                    table.add_column("Repository", style="cyan")
                    table.add_column("File", style="yellow")
                    table.add_column("Line", style="green")
                    table.add_column("Preview", style="white")
                    
                    for result in results[:10]:  # Limit to first 10 results
                        table.add_row(
                            str(result.get("repository", "N/A")),
                            result.get("file", "N/A"),
                            str(result.get("line", "N/A")),
                            result.get("preview", "N/A")[:50] + "..." if len(result.get("preview", "")) > 50 else result.get("preview", "N/A")
                        )
                    
                    console.print(table)
                else:
                    console.print("[yellow]No results found for your search query[/yellow]")
                    
            except Exception as e:
                console.print(f"[red]Search error: {e}[/red]")
            finally:
                await client.close()

    async def handle_view_command(self, args: list):
        """Handle view command to display file content from repositories."""
        if len(args) < 3:
            console.print("[red]Usage: /view <service> <owner/repo> <path>[/red]")
            console.print("[dim]Example: /view github facebook/react src/React.js[/dim]")
            return
            
        service = args[0].lower()
        if service not in ["github", "gitlab"]:
            console.print("[red]Service must be 'github' or 'gitlab'[/red]")
            return
            
        owner_repo = args[1]
        if "/" not in owner_repo:
            console.print("[red]Repository must be in format 'owner/repo'[/red]")
            return
            
        owner, repo = owner_repo.split("/", 1)
        file_path = args[2]
        
        await self.view_file_content(service, owner, repo, file_path)

    async def view_file_content(self, service: str, owner: str, repo: str, file_path: str):
        """View file content from GitHub or GitLab repository."""
        mcp_config = self.config.get_mcp_config()
        
        if service == "github":
            token = mcp_config.github.auth_token
            if not token:
                console.print("[red]GitHub not configured. Use /mcp add to set up GitHub first.[/red]")
                return
                
            client = SimpleGitHubClient(token)
            try:
                console.print(f"[blue]Fetching file: {owner}/{repo}/{file_path}[/blue]")
                
                file_data = await client.get_file_content(owner, repo, file_path)
                
                if "error" in file_data:
                    console.print(f"[red]Failed to fetch file: {file_data['error']}[/red]")
                    return
                
                content = file_data.get("content", "")
                file_info = f"**File:** {file_data.get('name', 'Unknown')}\n"
                file_info += f"**Path:** {file_data.get('path', 'Unknown')}\n"
                file_info += f"**Size:** {file_data.get('size', 0)} bytes\n"
                file_info += f"**URL:** {file_data.get('url', 'N/A')}\n\n"
                
                console.print(Panel(file_info, title=f"File Info - {owner}/{repo}", border_style="blue"))
                
                # Display code with syntax highlighting
                try:
                    from rich.syntax import Syntax
                    # Try to detect language from file extension
                    language = "text"
                    if "." in file_path:
                        ext = file_path.split(".")[-1].lower()
                        language_map = {
                            "py": "python", "js": "javascript", "ts": "typescript",
                            "java": "java", "cpp": "cpp", "c": "c", "go": "go",
                            "rs": "rust", "rb": "ruby", "php": "php", "html": "html",
                            "css": "css", "json": "json", "xml": "xml", "yaml": "yaml",
                            "yml": "yaml", "md": "markdown", "sh": "bash"
                        }
                        language = language_map.get(ext, "text")
                    
                    syntax = Syntax(content, language, theme="monokai", line_numbers=True)
                    console.print(syntax)
                except ImportError:
                    console.print(Panel(content, title="File Content", border_style="green"))
                    
            except Exception as e:
                console.print(f"[red]Error viewing file: {e}[/red]")
            finally:
                await client.close()
                
        elif service == "gitlab":
            token = mcp_config.gitlab.auth_token
            if not token:
                console.print("[red]GitLab not configured. Use /mcp add to set up GitLab first.[/red]")
                return
                
            client = SimpleGitLabClient(token, mcp_config.gitlab.base_url)
            try:
                console.print(f"[blue]Fetching file: {owner}/{repo}/{file_path}[/blue]")
                
                file_data = await client.get_file_content(owner, repo, file_path)
                
                if "error" in file_data:
                    console.print(f"[red]Failed to fetch file: {file_data['error']}[/red]")
                    return
                
                content = file_data.get("content", "")
                file_info = f"**File:** {file_data.get('file_name', 'Unknown')}\n"
                file_info += f"**Path:** {file_data.get('file_path', 'Unknown')}\n"
                file_info += f"**Size:** {file_data.get('size', 0)} bytes\n\n"
                
                console.print(Panel(file_info, title=f"File Info - {owner}/{repo}", border_style="blue"))
                
                # Display code with syntax highlighting
                try:
                    from rich.syntax import Syntax
                    # Try to detect language from file extension
                    language = "text"
                    if "." in file_path:
                        ext = file_path.split(".")[-1].lower()
                        language_map = {
                            "py": "python", "js": "javascript", "ts": "typescript",
                            "java": "java", "cpp": "cpp", "c": "c", "go": "go",
                            "rs": "rust", "rb": "ruby", "php": "php", "html": "html",
                            "css": "css", "json": "json", "xml": "xml", "yaml": "yaml",
                            "yml": "yaml", "md": "markdown", "sh": "bash"
                        }
                        language = language_map.get(ext, "text")
                    
                    syntax = Syntax(content, language, theme="monokai", line_numbers=True)
                    console.print(syntax)
                except ImportError:
                    console.print(Panel(content, title="File Content", border_style="green"))
                    
            except Exception as e:
                console.print(f"[red]Error viewing file: {e}[/red]")
            finally:
                await client.close()

    async def handle_analyze_command(self, args: list):
        """Handle analyze command to search and analyze code with AI."""
        if len(args) < 3:
            console.print("[red]Usage: /analyze <service> <question> --query <search_query> [--owner <owner>] [--repo <repo>] [--provider <provider>][/red]")
            console.print("[dim]Example: /analyze github \"How does authentication work?\" --query \"login function\"[/dim]")
            return
            
        service = args[0].lower()
        if service not in ["github", "gitlab"]:
            console.print("[red]Service must be 'github' or 'gitlab'[/red]")
            return
            
        question = args[1]
        
        # Parse remaining arguments
        query = None
        owner = None
        repo = None
        provider = self.config.default_provider
        
        i = 2
        while i < len(args):
            if args[i] == "--query" and i + 1 < len(args):
                query = args[i + 1]
                i += 2
            elif args[i] == "--owner" and i + 1 < len(args):
                owner = args[i + 1]
                i += 2
            elif args[i] == "--repo" and i + 1 < len(args):
                repo = args[i + 1]
                i += 2
            elif args[i] == "--provider" and i + 1 < len(args):
                provider = args[i + 1]
                i += 2
            else:
                i += 1
        
        if not query:
            console.print("[red]--query parameter is required[/red]")
            return
        
        await self.analyze_code_with_ai(service, question, query, owner, repo, provider)

    async def analyze_code_with_ai(self, service: str, question: str, query: str, owner: str = None, repo: str = None, provider: str = None):
        """Search for code and analyze it with AI."""
        console.print(f"[blue]Searching {service} for: {query}[/blue]")
        
        # First, search for relevant code
        mcp_config = self.config.get_mcp_config()
        
        if service == "github":
            token = mcp_config.github.auth_token
            if not token:
                console.print("[red]GitHub not configured. Use /mcp add to set up GitHub first.[/red]")
                return
                
            client = SimpleGitHubClient(token)
            try:
                results_data = await client.search_code(query, owner, repo)
                
                if "error" in results_data:
                    console.print(f"[red]Search failed: {results_data['error']}[/red]")
                    return
                
                results = results_data.get("results", [])
                
                if not results:
                    console.print("[yellow]No code found for your search query.[/yellow]")
                    return
                
                # Get content from the top few results
                code_context = []
                console.print(f"[blue]Found {len(results)} search results. Fetching content from top 3...[/blue]")
                
                for i, result in enumerate(results[:3]):  # Limit to top 3 results
                    console.print(f"[dim]Fetching {result['repository']}/{result['path']}...[/dim]")
                    
                    file_data = await client.get_file_content(
                        result["owner"], 
                        result["repo_name"], 
                        result["path"]
                    )
                    
                    if "content" in file_data:
                        content = file_data["content"][:2000]  # Limit content size
                        code_context.append({
                            "repository": result["repository"],
                            "file": result["file"],
                            "path": result["path"],
                            "url": result["url"],
                            "content": content
                        })
                        console.print(f"[green]✓ Got {len(content)} chars from {result['file']}[/green]")
                    else:
                        console.print(f"[yellow]⚠ Could not fetch content from {result['file']}: {file_data.get('error', 'Unknown error')}[/yellow]")
                
                console.print(f"[blue]Retrieved content from {len(code_context)} files.[/blue]")
                
                await client.close()
                
            except Exception as e:
                console.print(f"[red]Search error: {e}[/red]")
                await client.close()
                return
                
        elif service == "gitlab":
            token = mcp_config.gitlab.auth_token
            if not token:
                console.print("[red]GitLab not configured. Use /mcp add to set up GitLab first.[/red]")
                return
            
            client = SimpleGitLabClient(token, mcp_config.gitlab.base_url)
            try:
                results_data = await client.search_code(query, owner, repo)
                
                if "error" in results_data:
                    console.print(f"[red]Search failed: {results_data['error']}[/red]")
                    return
                
                results = results_data.get("results", [])
                
                if not results:
                    console.print("[yellow]No code found for your search query.[/yellow]")
                    return
                
                # For GitLab, we already have previews in the search results
                code_context = []
                for result in results[:5]:  # Use more results since we have less content
                    code_context.append({
                        "repository": result["repository"],
                        "file": result["file"],
                        "path": result.get("path", "N/A"),
                        "line": result.get("line", "N/A"),
                        "content": result.get("preview", "No preview available")
                    })
                
                await client.close()
                
            except Exception as e:
                console.print(f"[red]Search error: {e}[/red]")
                await client.close()
                return
        
        # Now analyze with AI
        if code_context:
            await self.send_analysis_to_ai(question, code_context, provider or self.config.default_provider)
        else:
            console.print("[yellow]No code content available for analysis.[/yellow]")

    async def send_analysis_to_ai(self, question: str, code_context: list, provider: str):
        """Send code context and question to AI for analysis."""
        
        # Show user what code we're analyzing
        console.print(f"\n[bold blue]Code Sources Being Analyzed:[/bold blue]")
        for i, context in enumerate(code_context, 1):
            console.print(f"{i}. {context['repository']}/{context['path']}")
        console.print()
        
        # Prepare the context message
        context_message = f"User Question: {question}\n\n"
        context_message += "Here is the relevant code I found from real repositories:\n\n"
        
        for i, context in enumerate(code_context, 1):
            context_message += f"## Code Example {i}\n"
            context_message += f"**Repository:** {context['repository']}\n"
            context_message += f"**File:** {context['file']}\n"
            context_message += f"**Path:** {context['path']}\n"
            if context.get('url'):
                context_message += f"**URL:** {context['url']}\n"
            if context.get('line'):
                context_message += f"**Line:** {context['line']}\n"
            context_message += f"\n```\n{context['content']}\n```\n\n"
        
        context_message += "Based on the ACTUAL CODE above from these repositories, please:\n"
        context_message += "1. Analyze the code and answer the user's question\n"
        context_message += "2. Provide specific examples from the code above\n"
        context_message += "3. Explain how the code works with concrete implementation details\n"
        context_message += "4. Include relevant code snippets in your response\n"
        context_message += "5. Cite the source files and repositories\n"
        context_message += "6. Give step-by-step implementation guidance based on the real code patterns shown"
        
        try:
            provider_config = self.config.get_provider_config(provider).model_dump()
            ai_provider = ProviderFactory.create_provider(provider, provider_config)
            
            async with ai_provider:
                messages = [AIMessage(role="user", content=context_message)]
                
                console.print(f"[blue]Analyzing code with {provider}...[/blue]")
                
                with console.status(f"Getting analysis from {provider}..."):
                    response = await ai_provider.chat_completion(messages)
                
                console.print(f"\n[bold green]AI Analysis ({provider}):[/bold green]")
                console.print()
                console.print(Markdown(response.content))
                
                if response.usage:
                    console.print(f"\n[dim]Tokens used: {response.usage}[/dim]")
                    
        except Exception as e:
            console.print(f"[red]AI Analysis error: {e}[/red]")

    async def handle_providers_command(self):
        """Show AI provider status."""
        table = Table(title="AI Providers Status")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Models", style="yellow")
        
        available_providers = ProviderFactory.get_available_providers()
        
        for provider_name in available_providers:
            try:
                provider_config = self.config.get_provider_config(provider_name).model_dump()
                provider = ProviderFactory.create_provider(provider_name, provider_config)
                
                async with provider:
                    is_valid = await provider.validate_connection()
                    status = "✓ Connected" if is_valid else "✗ Disconnected"
                    models = ", ".join(provider.supported_models[:3])
                    if len(provider.supported_models) > 3:
                        models += f" (+{len(provider.supported_models) - 3} more)"
                    
                    table.add_row(provider_name, status, models)
                    
            except Exception as e:
                table.add_row(provider_name, f"✗ Error: {str(e)[:30]}...", "N/A")
        
        console.print(table)

    def handle_config_command(self):
        """Show current configuration."""
        console.print(Panel(
            f"Config Directory: {self.config.config_dir}\n"
            f"Default Provider: {self.config.default_provider}\n"
            f"Log Level: {self.config.log_level}\n"
            f"Providers: {list(self.config.providers.keys())}\n"
            f"MCP Services: {list(self.config.mcp.keys())}",
            title="AI CLI Configuration"
        ))

    async def handle_chat_message(self, message: str):
        """Handle chat message to AI providers."""
        # Parse message for flags
        parts = message.split()
        provider = self.config.default_provider
        stream = False
        
        # Simple flag parsing
        clean_parts = []
        i = 0
        while i < len(parts):
            if parts[i] == "--provider" and i + 1 < len(parts):
                provider = parts[i + 1]
                i += 2
            elif parts[i] == "--stream":
                stream = True
                i += 1
            else:
                clean_parts.append(parts[i])
                i += 1
        
        clean_message = " ".join(clean_parts)
        
        if not clean_message.strip():
            console.print("[yellow]Please enter a message to send to the AI.[/yellow]")
            return
            
        try:
            provider_config = self.config.get_provider_config(provider).model_dump()
            ai_provider = ProviderFactory.create_provider(provider, provider_config)
            
            async with ai_provider:
                messages = [AIMessage(role="user", content=clean_message)]
                
                if stream:
                    console.print(f"[bold blue]{provider}[/bold blue] streaming response:")
                    console.print()
                    
                    async for chunk in ai_provider.stream_completion(messages):
                        console.print(chunk, end="")
                    console.print()
                else:
                    with console.status(f"Getting response from {provider}..."):
                        response = await ai_provider.chat_completion(messages)
                    
                    console.print(f"[bold blue]{provider}[/bold blue] response:")
                    console.print()
                    console.print(Markdown(response.content))
                    
                    if response.usage:
                        console.print(f"\n[dim]Tokens used: {response.usage}[/dim]")
                        
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    async def handle_local_command(self, args: list):
        """Handle local codebase search and analysis."""
        if not args:
            console.print("[red]Usage: /local <query> [--path <path>] [--provider <provider>] [--ext <extensions>][/red]")
            console.print("[dim]Example: /local \"websocket architecture\"[/dim]")
            console.print("[dim]Example: /local \"authentication\" --path ./src --ext js,ts,py[/dim]")
            return
            
        query = args[0]
        
        # Parse remaining arguments
        search_path = "."
        provider = self.config.default_provider
        extensions = None
        
        i = 1
        while i < len(args):
            if args[i] == "--path" and i + 1 < len(args):
                search_path = args[i + 1]
                i += 2
            elif args[i] == "--provider" and i + 1 < len(args):
                provider = args[i + 1]
                i += 2
            elif args[i] == "--ext" and i + 1 < len(args):
                extensions = args[i + 1].split(",")
                i += 2
            else:
                i += 1
        
        await self.search_local_codebase(query, search_path, provider, extensions)

    def search_files_with_ripgrep(self, query: str, search_path: str = ".", extensions: List[str] = None) -> List[Dict[str, Any]]:
        """Search files using ripgrep for better performance."""
        try:
            # Build ripgrep command
            cmd = ["rg", "--json", "--smart-case", "--max-count", "5", query]
            
            if extensions:
                for ext in extensions:
                    cmd.extend(["--type-add", f"custom:*.{ext.strip()}", "--type", "custom"])
            
            # Add path
            cmd.append(search_path)
            
            # Run ripgrep
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0 and result.returncode != 1:  # 1 means no matches found
                console.print(f"[yellow]Ripgrep error: {result.stderr}[/yellow]")
                return self.search_files_with_grep(query, search_path, extensions)
            
            # Parse JSON output
            matches = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    import json
                    data = json.loads(line)
                    if data.get('type') == 'match':
                        match_data = data['data']
                        matches.append({
                            'file': match_data['path']['text'],
                            'line_number': match_data['line_number'],
                            'line_content': match_data['lines']['text'],
                            'absolute_offset': match_data.get('absolute_offset', 0)
                        })
                except (json.JSONDecodeError, KeyError):
                    continue
            
            return matches
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback to grep
            return self.search_files_with_grep(query, search_path, extensions)

    def search_files_with_grep(self, query: str, search_path: str = ".", extensions: List[str] = None) -> List[Dict[str, Any]]:
        """Fallback search using grep."""
        try:
            cmd = ["grep", "-r", "-n", "-i", "--max-count=5"]
            
            if extensions:
                for ext in extensions:
                    cmd.extend(["--include", f"*.{ext.strip()}"])
            
            cmd.extend([query, search_path])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            matches = []
            for line in result.stdout.strip().split('\n'):
                if ':' in line:
                    parts = line.split(':', 2)
                    if len(parts) >= 3:
                        matches.append({
                            'file': parts[0],
                            'line_number': int(parts[1]) if parts[1].isdigit() else 0,
                            'line_content': parts[2],
                            'absolute_offset': 0
                        })
            
            return matches
            
        except (subprocess.TimeoutExpired, Exception):
            return []

    def get_file_content_around_match(self, file_path: str, line_number: int, context_lines: int = 10) -> str:
        """Get file content around a specific line."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            start = max(0, line_number - context_lines - 1)
            end = min(len(lines), line_number + context_lines)
            
            context = []
            for i in range(start, end):
                prefix = ">>> " if i == line_number - 1 else "    "
                context.append(f"{prefix}{i+1:4}: {lines[i].rstrip()}")
            
            return '\n'.join(context)
            
        except Exception as e:
            return f"Error reading file: {e}"

    async def search_local_codebase(self, query: str, search_path: str = ".", provider: str = None, extensions: List[str] = None):
        """Search local codebase and analyze with AI."""
        console.print(f"[blue]Searching local codebase for: {query}[/blue]")
        console.print(f"[dim]Path: {search_path}[/dim]")
        if extensions:
            console.print(f"[dim]Extensions: {', '.join(extensions)}[/dim]")
        
        # Search for files
        matches = self.search_files_with_ripgrep(query, search_path, extensions)
        
        if not matches:
            console.print("[yellow]No matches found in local codebase.[/yellow]")
            return
        
        console.print(f"[green]Found {len(matches)} matches in local files:[/green]")
        
        # Show search results
        table = Table(title="Local Search Results")
        table.add_column("File", style="cyan")
        table.add_column("Line", style="yellow")
        table.add_column("Preview", style="white")
        
        code_context = []
        file_contents = {}
        
        for match in matches[:10]:  # Limit to top 10 matches
            file_path = match['file']
            line_num = match['line_number']
            preview = match['line_content'][:80] + "..." if len(match['line_content']) > 80 else match['line_content']
            
            table.add_row(
                file_path,
                str(line_num),
                preview.strip()
            )
            
            # Get context around the match
            if file_path not in file_contents:
                context = self.get_file_content_around_match(file_path, line_num, context_lines=15)
                file_contents[file_path] = context
                
                code_context.append({
                    'file': file_path,
                    'line': line_num,
                    'content': context,
                    'match_line': match['line_content'].strip()
                })
        
        console.print(table)
        
        # Analyze with AI
        if code_context:
            console.print(f"\n[blue]Analyzing {len(code_context)} code sections with AI...[/blue]")
            await self.analyze_local_code_with_ai(query, code_context, provider or self.config.default_provider)
        else:
            console.print("[yellow]No code content available for analysis.[/yellow]")

    async def analyze_local_code_with_ai(self, query: str, code_context: List[Dict[str, Any]], provider: str):
        """Analyze local code with AI."""
        
        # Show what we're analyzing
        console.print(f"\n[bold blue]Analyzing Local Code Files:[/bold blue]")
        for i, context in enumerate(code_context, 1):
            console.print(f"{i}. {context['file']}:{context['line']}")
        console.print()
        
        # Prepare context message
        context_message = f"User Query: {query}\n\n"
        context_message += "I found the following code in the local codebase that matches your query:\n\n"
        
        for i, context in enumerate(code_context, 1):
            context_message += f"## File {i}: {context['file']}\n"
            context_message += f"**Match on line {context['line']}:** `{context['match_line']}`\n\n"
            context_message += "**Code Context:**\n"
            context_message += f"```\n{context['content']}\n```\n\n"
        
        context_message += "Based on the ACTUAL CODE from this local codebase, please:\n"
        context_message += "1. Answer the user's query with specific examples from the code above\n"
        context_message += "2. Explain how the code works and any patterns you see\n"
        context_message += "3. Provide implementation guidance based on the existing code\n"
        context_message += "4. Suggest improvements or best practices\n"
        context_message += "5. Reference specific files and line numbers in your response\n"
        context_message += "6. If the query is about architecture, explain the overall structure you can infer from these examples"
        
        try:
            provider_config = self.config.get_provider_config(provider).model_dump()
            ai_provider = ProviderFactory.create_provider(provider, provider_config)
            
            async with ai_provider:
                messages = [AIMessage(role="user", content=context_message)]
                
                console.print(f"[blue]Getting analysis from {provider}...[/blue]")
                
                with console.status(f"Analyzing local code with {provider}..."):
                    response = await ai_provider.chat_completion(messages)
                
                console.print(f"\n[bold green]Local Code Analysis ({provider}):[/bold green]")
                console.print()
                console.print(Markdown(response.content))
                
                if response.usage:
                    console.print(f"\n[dim]Tokens used: {response.usage}[/dim]")
                    
        except Exception as e:
            console.print(f"[red]AI Analysis error: {e}[/red]")

    async def run(self):
        """Main interactive loop."""
        self.show_welcome()
        
        while self.running:
            try:
                user_input = Prompt.ask("\n[bold cyan]AI CLI[/bold cyan]", default="").strip()
                
                if not user_input:
                    continue
                    
                # Handle commands
                if user_input.startswith("/"):
                    try:
                        # Use shlex to properly parse quoted strings
                        command_parts = shlex.split(user_input[1:])
                        command = command_parts[0].lower()
                        args = command_parts[1:] if len(command_parts) > 1 else []
                    except ValueError as e:
                        console.print(f"[red]Invalid command syntax: {e}[/red]")
                        continue
                    
                    if command in ["exit", "quit", "q"]:
                        console.print("[green]Goodbye! 👋[/green]")
                        self.running = False
                    elif command == "help":
                        self.show_help()
                    elif command == "setup":
                        await self.handle_setup_command(args)
                    elif command == "mcp":
                        await self.handle_mcp_command(args)
                    elif command == "search":
                        await self.handle_search_command(args)
                    elif command == "local":
                        await self.handle_local_command(args)
                    elif command == "view":
                        await self.handle_view_command(args)
                    elif command == "analyze":
                        await self.handle_analyze_command(args)
                    elif command == "providers":
                        await self.handle_providers_command()
                    elif command == "config":
                        self.handle_config_command()
                    else:
                        console.print(f"[red]Unknown command: /{command}[/red]")
                        console.print("[dim]Type /help for available commands[/dim]")
                else:
                    # Handle as chat message
                    await self.handle_chat_message(user_input)
                    
            except KeyboardInterrupt:
                console.print("\n[green]Goodbye! 👋[/green]")
                self.running = False
            except Exception as e:
                console.print(f"[red]Unexpected error: {e}[/red]")


async def main():
    """Main entry point for interactive mode."""
    cli = InteractiveCLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())