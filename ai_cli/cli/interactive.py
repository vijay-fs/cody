import asyncio
from typing import Optional
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
                provider_config = self.config.get_provider_config(provider_name).dict()
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

    async def handle_providers_command(self):
        """Show AI provider status."""
        table = Table(title="AI Providers Status")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Models", style="yellow")
        
        available_providers = ProviderFactory.get_available_providers()
        
        for provider_name in available_providers:
            try:
                provider_config = self.config.get_provider_config(provider_name).dict()
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
            provider_config = self.config.get_provider_config(provider).dict()
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
                    command_parts = user_input[1:].split()
                    command = command_parts[0].lower()
                    args = command_parts[1:] if len(command_parts) > 1 else []
                    
                    if command in ["exit", "quit", "q"]:
                        console.print("[green]Goodbye! 👋[/green]")
                        self.running = False
                    elif command == "help":
                        self.show_help()
                    elif command == "setup":
                        await self.handle_setup_command(args)
                    elif command == "mcp":
                        await self.handle_mcp_command(args)
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