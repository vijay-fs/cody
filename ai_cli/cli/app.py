#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from ..core.config import AICliConfig
from .interactive import main as interactive_main
from .main import _chat_async, _providers_async, _mcp_connect_async, _mcp_search_async

console = Console()

app = typer.Typer(
    name="ai",
    help="AI CLI - Interactive AI assistant with MCP integration",
    rich_markup_mode="rich"
)

# Global config instance
config = AICliConfig()


def version_callback(value: bool):
    if value:
        console.print("AI CLI v0.1.0")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, 
        "--version", 
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True
    ),
    config_dir: Optional[Path] = typer.Option(
        None,
        "--config-dir",
        help="Configuration directory path"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Enable verbose logging"
    )
):
    """
    AI CLI - Interactive AI assistant with MCP integration.
    
    Run without arguments to enter interactive mode.
    Use 'ai --help' to see all available commands.
    """
    global config
    
    if config_dir:
        config.config_dir = config_dir
    
    if verbose:
        config.log_level = "DEBUG"
        
    config.load_config_file()
    
    # If no subcommand is provided, enter interactive mode
    if ctx.invoked_subcommand is None:
        console.print("[dim]Starting interactive mode... (use --help for commands)[/dim]")
        asyncio.run(interactive_main())


@app.command("chat")
def chat_command(
    message: str = typer.Argument(..., help="Message to send to AI"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="AI provider"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use"),
    stream: bool = typer.Option(False, "--stream", "-s", help="Stream response"),
    max_tokens: Optional[int] = typer.Option(None, "--max-tokens", help="Maximum tokens"),
    temperature: Optional[float] = typer.Option(None, "--temperature", "-t", help="Temperature")
):
    """Send a single chat message (non-interactive mode)."""
    asyncio.run(_chat_async(message, provider, model, stream, max_tokens, temperature))


@app.command("interactive")
def interactive_command():
    """Enter interactive mode explicitly."""
    asyncio.run(interactive_main())


@app.command("providers")
def providers_command():
    """List available AI providers and their status."""
    asyncio.run(_providers_async())


@app.command("config")
def config_command(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    edit: bool = typer.Option(False, "--edit", help="Edit configuration file"),
    init: bool = typer.Option(False, "--init", help="Initialize configuration")
):
    """Manage configuration."""
    if init:
        config.save_config_file()
        console.print(f"[green]Configuration initialized at {config.config_dir / 'config.yaml'}[/green]")
    elif show:
        from rich.panel import Panel
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


# MCP commands subgroup
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


@mcp_app.command("search")
def mcp_search(
    service: str = typer.Argument(..., help="Service to search (gitlab, github)"),
    query: str = typer.Argument(..., help="Search query"),
    owner: Optional[str] = typer.Option(None, "--owner", help="Repository owner"),
    repo: Optional[str] = typer.Option(None, "--repo", help="Repository name")
):
    """Search code in connected MCP services."""
    asyncio.run(_mcp_search_async(service, query, owner, repo))


if __name__ == "__main__":
    app()