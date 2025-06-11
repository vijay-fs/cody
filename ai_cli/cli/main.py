import asyncio
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from ..core.config import AICliConfig
from ..providers.factory import ProviderFactory
from ..providers.base import AIMessage
try:
    from ..mcp.client import MCPClient
    MCP_AVAILABLE = True
except ImportError:
    from ..mcp.simple_client import SimpleGitHubClient, SimpleGitLabClient
    MCP_AVAILABLE = False

app = typer.Typer(
    name="ai-cli",
    help="Scalable CLI tool for multiple AI providers with MCP integration",
    rich_markup_mode="rich"
)
console = Console()

# Global config instance
config = AICliConfig()


@app.callback()
def main(
    ctx: typer.Context,
    config_dir: Optional[Path] = typer.Option(
        None,
        "--config-dir",
        help="Configuration directory path"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging"
    )
):
    """AI CLI - Multi-provider AI assistant with MCP integration."""
    global config
    
    if config_dir:
        config.config_dir = config_dir
    
    if verbose:
        config.log_level = "DEBUG"
        
    config.load_config_file()


@app.command()
def chat(
    message: str = typer.Argument(..., help="Message to send to AI"),
    provider: Optional[str] = typer.Option(
        None,
        "--provider",
        "-p",
        help="AI provider to use"
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Model to use"
    ),
    stream: bool = typer.Option(
        False,
        "--stream",
        "-s",
        help="Stream response"
    ),
    max_tokens: Optional[int] = typer.Option(
        None,
        "--max-tokens",
        help="Maximum tokens in response"
    ),
    temperature: Optional[float] = typer.Option(
        None,
        "--temperature",
        "-t",
        help="Temperature for response generation"
    )
):
    """Send a chat message to an AI provider."""
    asyncio.run(_chat_async(
        message, provider, model, stream, max_tokens, temperature
    ))


async def _chat_async(
    message: str,
    provider: Optional[str],
    model: Optional[str],
    stream: bool,
    max_tokens: Optional[int],
    temperature: Optional[float]
):
    provider_name = provider or config.default_provider
    
    try:
        provider_config = config.get_provider_config(provider_name).dict()
        ai_provider = ProviderFactory.create_provider(provider_name, provider_config)
        
        async with ai_provider:
            messages = [AIMessage(role="user", content=message)]
            
            kwargs = {}
            if model:
                kwargs["model"] = model
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            if temperature:
                kwargs["temperature"] = temperature
            
            if stream:
                console.print(f"[bold blue]{provider_name}[/bold blue] streaming response:")
                console.print()
                
                async for chunk in ai_provider.stream_completion(messages, **kwargs):
                    console.print(chunk, end="")
                console.print()
            else:
                with console.status(f"Getting response from {provider_name}..."):
                    response = await ai_provider.chat_completion(messages, **kwargs)
                
                console.print(f"[bold blue]{provider_name}[/bold blue] response:")
                console.print()
                console.print(Markdown(response.content))
                
                if response.usage:
                    console.print(f"\n[dim]Tokens used: {response.usage}[/dim]")
                    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def providers():
    """List available AI providers and their status."""
    asyncio.run(_providers_async())


async def _providers_async():
    table = Table(title="Available AI Providers")
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Models", style="yellow")
    
    available_providers = ProviderFactory.get_available_providers()
    
    for provider_name in available_providers:
        try:
            provider_config = config.get_provider_config(provider_name).dict()
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


mcp_app = typer.Typer(name="mcp", help="MCP (Model Context Protocol) commands")
app.add_typer(mcp_app, name="mcp")


@mcp_app.command("connect")
def mcp_connect(
    service: str = typer.Argument(..., help="Service to connect (gitlab, github)"),
    token: str = typer.Option(..., "--token", help="Authentication token"),
    url: Optional[str] = typer.Option(None, "--url", help="Base URL for service")
):
    """Connect to an MCP service."""
    asyncio.run(_mcp_connect_async(service, token, url))


async def _mcp_connect_async(service: str, token: str, url: Optional[str]):
    if MCP_AVAILABLE:
        async with MCPClient() as mcp_client:
            try:
                if service == "gitlab":
                    await mcp_client.connect_gitlab(token, url or "https://gitlab.com")
                elif service == "github":
                    await mcp_client.connect_github(token, url or "https://api.github.com")
                else:
                    console.print(f"[red]Unknown service: {service}[/red]")
                    raise typer.Exit(1)
                
                console.print(f"[green]Successfully connected to {service}[/green]")
                
                # Test connection by listing resources
                resources = await mcp_client.list_resources(service)
                console.print(f"Available resources: {len(resources)}")
                
            except Exception as e:
                console.print(f"[red]Connection failed: {e}[/red]")
                raise typer.Exit(1)
    else:
        # Use simplified client
        try:
            if service == "github":
                client = SimpleGitHubClient(token)
                try:
                    is_valid = await client.validate_connection()
                    if is_valid:
                        console.print(f"[green]Successfully connected to {service}[/green]")
                        repos = await client.get_user_repos()
                        console.print(f"Found {len(repos)} repositories")
                    else:
                        console.print(f"[red]Failed to connect to {service}[/red]")
                        raise typer.Exit(1)
                finally:
                    await client.close()
            elif service == "gitlab":
                client = SimpleGitLabClient(token, url or "https://gitlab.com")
                try:
                    is_valid = await client.validate_connection()
                    if is_valid:
                        console.print(f"[green]Successfully connected to {service}[/green]")
                    else:
                        console.print(f"[red]Failed to connect to {service}[/red]")
                        raise typer.Exit(1)
                finally:
                    await client.close()
            else:
                console.print(f"[red]Unknown service: {service}[/red]")
                raise typer.Exit(1)
                
        except Exception as e:
            console.print(f"[red]Connection failed: {e}[/red]")
            raise typer.Exit(1)


@mcp_app.command("search")
def mcp_search(
    service: str = typer.Argument(..., help="Service to search (gitlab, github)"),
    query: str = typer.Argument(..., help="Search query"),
    owner: Optional[str] = typer.Option(None, "--owner", help="Repository owner"),
    repo: Optional[str] = typer.Option(None, "--repo", help="Repository name")
):
    """Search code in connected MCP services."""
    asyncio.run(_mcp_search_async(service, query, owner, repo))


async def _mcp_search_async(
    service: str, 
    query: str, 
    owner: Optional[str], 
    repo: Optional[str]
):
    mcp_config = config.get_mcp_config()
    
    if MCP_AVAILABLE:
        async with MCPClient() as mcp_client:
            try:
                if service == "gitlab":
                    gitlab_config = mcp_config.gitlab
                    await mcp_client.connect_gitlab(
                        gitlab_config.auth_token, 
                        gitlab_config.base_url
                    )
                elif service == "github":
                    github_config = mcp_config.github
                    await mcp_client.connect_github(
                        github_config.auth_token, 
                        github_config.base_url
                    )
                
                results = await mcp_client.search_code(service, query, owner, repo)
                
                if results:
                    table = Table(title=f"Search Results from {service}")
                    table.add_column("Repository", style="cyan")
                    table.add_column("File", style="yellow")
                    table.add_column("Line", style="green")
                    table.add_column("Preview", style="white")
                    
                    for result in results[:10]:  # Limit to first 10 results
                        table.add_row(
                            result.get("repository", "N/A"),
                            result.get("file", "N/A"),
                            str(result.get("line", "N/A")),
                            result.get("preview", "N/A")[:50] + "..."
                        )
                    
                    console.print(table)
                else:
                    console.print("[yellow]No results found[/yellow]")
                    
            except Exception as e:
                console.print(f"[red]Search failed: {e}[/red]")
                raise typer.Exit(1)
    else:
        # Use simplified client
        try:
            if service == "github":
                github_config = mcp_config.github
                client = SimpleGitHubClient(github_config.auth_token)
                try:
                    results_data = await client.search_code(query, owner, repo)
                    
                    if "error" in results_data:
                        console.print(f"[red]Search failed: {results_data['error']}[/red]")
                        raise typer.Exit(1)
                    
                    results = results_data.get("results", [])
                    total_count = results_data.get("total_count", 0)
                    
                    if results:
                        table = Table(title=f"Search Results from {service} (Total: {total_count})")
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
                    else:
                        console.print("[yellow]No results found[/yellow]")
                finally:
                    await client.close()
                        
            elif service == "gitlab":
                gitlab_config = mcp_config.gitlab
                client = SimpleGitLabClient(gitlab_config.auth_token, gitlab_config.base_url)
                try:
                    results_data = await client.search_code(query, owner, repo)
                    
                    if "error" in results_data:
                        console.print(f"[red]Search failed: {results_data['error']}[/red]")
                        raise typer.Exit(1)
                    
                    results = results_data.get("results", [])
                    
                    if results:
                        table = Table(title=f"Search Results from {service}")
                        table.add_column("Repository", style="cyan")
                        table.add_column("File", style="yellow")
                        table.add_column("Line", style="green")
                        table.add_column("Preview", style="white")
                        
                        for result in results[:10]:  # Limit to first 10 results
                            table.add_row(
                                str(result.get("repository", "N/A")),
                                result.get("file", "N/A"),
                                str(result.get("line", "N/A")),
                                result.get("preview", "N/A")[:50] + "..."
                            )
                        
                        console.print(table)
                    else:
                        console.print("[yellow]No results found[/yellow]")
                finally:
                    await client.close()
            else:
                console.print(f"[red]Unknown service: {service}[/red]")
                raise typer.Exit(1)
                
        except Exception as e:
            console.print(f"[red]Search failed: {e}[/red]")
            raise typer.Exit(1)


@app.command()
def config_cmd(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    edit: bool = typer.Option(False, "--edit", help="Edit configuration file"),
    init: bool = typer.Option(False, "--init", help="Initialize configuration")
):
    """Manage configuration."""
    if init:
        config.save_config_file()
        console.print(f"[green]Configuration initialized at {config.config_dir / 'config.yaml'}[/green]")
    
    elif show:
        console.print(Panel(
            f"Config Directory: {config.config_dir}\n"
            f"Default Provider: {config.default_provider}\n"
            f"Log Level: {config.log_level}\n"
            f"Providers: {list(config.providers.keys())}\n"
            f"MCP Services: {list(config.mcp.keys())}",
            title="AI CLI Configuration"
        ))
    
    elif edit:
        config_file = config.config_dir / "config.yaml"
        typer.launch(str(config_file))
    
    else:
        console.print("[yellow]Use --show, --edit, or --init[/yellow]")


if __name__ == "__main__":
    app()