# AI CLI

A scalable command-line tool for interacting with multiple AI providers (OpenAI, Claude, Azure OpenAI, Ollama) with Model Context Protocol (MCP) integration for seamless access to GitLab and GitHub repositories.

## 🚀 Features

- **Multi-Provider Support**: OpenAI, Claude (Anthropic), Azure OpenAI, and Ollama
- **MCP Integration**: Direct access to GitLab and GitHub repositories for code context
- **Streaming Responses**: Real-time response streaming for better user experience
- **Flexible Configuration**: YAML config files with environment variable overrides
- **Extensible Architecture**: Plugin-style provider system for easy expansion
- **Rich CLI Interface**: Beautiful terminal output with syntax highlighting
- **Security First**: Secure token storage and minimal permission requirements

## 📦 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-cli.git
cd ai-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

### Basic Usage

```bash
# Initialize configuration
ai-cli config-cmd --init

# Chat with default provider
ai-cli chat "Explain quantum computing"

# Use specific provider
ai-cli chat "Write a Python function" --provider claude

# Stream response
ai-cli chat "Tell me a story" --stream

# Connect to GitHub
ai-cli mcp connect github --token your-github-token

# Search code
ai-cli mcp search github "function main" --owner yourorg --repo yourproject
```

## 🎯 Quick Examples

### Basic AI Chat
```bash
# Simple chat
ai-cli chat "What is Python?"

# Chat with specific provider and parameters
ai-cli chat "Explain async programming" --provider claude --temperature 0.3 --max-tokens 1000

# Stream long responses
ai-cli chat "Write a detailed tutorial on Docker" --stream --provider openai
```

### Code Analysis with MCP
```bash
# Connect to GitHub
ai-cli mcp connect github --token ghp_your_token_here

# Search for authentication patterns
ai-cli mcp search github "authentication middleware" --owner myorg --repo webapp

# Analyze specific repository
ai-cli mcp search github "TODO|FIXME" --owner myorg --repo backend
ai-cli chat "Review these code issues and prioritize them" --provider claude
```

### Configuration Management
```bash
# Initialize and edit config
ai-cli config-cmd --init
ai-cli config-cmd --edit

# Check provider status
ai-cli providers

# View current settings
ai-cli config-cmd --show
```

## 🔧 Configuration

### Provider Setup

Edit `~/.config/ai-cli/config.yaml`:

```yaml
providers:
  openai:
    api_key: "sk-your-openai-key"
    model: "gpt-4"
  
  claude:
    api_key: "sk-ant-your-claude-key"
    model: "claude-3-sonnet-20240229"
  
  azure_openai:
    endpoint: "https://your-resource.openai.azure.com/"
    api_key: "your-azure-key"
    deployment_name: "gpt-4"
  
  ollama:
    base_url: "http://localhost:11434"
    model: "llama2"

mcp:
  gitlab:
    auth_token: "glpat-your-gitlab-token"
  github:
    auth_token: "ghp_your-github-token"

default_provider: "openai"
```

### Environment Variables

```bash
export AI_CLI_OPENAI_API_KEY="sk-your-key"
export AI_CLI_CLAUDE_API_KEY="sk-ant-your-key"
export AI_CLI_GITLAB_AUTH_TOKEN="glpat-your-token"
export AI_CLI_GITHUB_AUTH_TOKEN="ghp_your-token"
```

## 🛠️ Commands

### Chat

```bash
# Basic chat
ai-cli chat "Your message here"

# Options
ai-cli chat "Message" --provider claude --model claude-3-opus-20240229 --stream --max-tokens 2000 --temperature 0.8
```

### Providers

```bash
# List all providers and their status
ai-cli providers
```

### MCP Integration

```bash
# Connect to services
ai-cli mcp connect gitlab --token your-token
ai-cli mcp connect github --token your-token

# Search code
ai-cli mcp search github "search query" --owner org --repo repository
ai-cli mcp search gitlab "function name" --owner team --repo project
```

### Configuration

```bash
# Show current config
ai-cli config-cmd --show

# Edit config file
ai-cli config-cmd --edit

# Initialize new config
ai-cli config-cmd --init
```

## 🔌 MCP Integration

The CLI integrates with the Model Context Protocol to provide AI providers with access to your code repositories.

### Supported Services

- **GitLab**: Project access, code search, file retrieval, commit history
- **GitHub**: Repository browsing, advanced code search, file operations

### Example Workflow

```bash
# 1. Connect to GitHub
ai-cli mcp connect github --token ghp_your_token

# 2. Search for authentication code
ai-cli mcp search github "authentication" --owner myorg --repo webapp

# 3. Analyze with AI
ai-cli chat "Review this authentication code for security issues" --provider claude
```

## 🏗️ Architecture

```
CLI Layer (Typer)
    ↓
Provider Factory
    ↓
AI Providers (OpenAI, Claude, Azure, Ollama)
    ↓
MCP Client
    ↓
MCP Servers (GitLab, GitHub)
```

### Key Components

- **Provider Layer**: Unified interface for different AI providers
- **MCP Integration**: Protocol implementation for code repository access
- **Configuration Management**: Flexible YAML + environment variable configuration
- **CLI Interface**: Rich terminal interface with streaming support

## 🚀 Advanced Usage

### Multi-Provider Comparison

```bash
# Compare responses from different providers
ai-cli chat "Explain REST APIs" --provider openai > openai.txt
ai-cli chat "Explain REST APIs" --provider claude > claude.txt
```

### Code Analysis Pipeline

```bash
#!/bin/bash
# Automated code review script

REPO_OWNER="myorg"
REPO_NAME="myproject"

# Search for potential issues
ISSUES=$(ai-cli mcp search github "TODO|FIXME|HACK" --owner $REPO_OWNER --repo $REPO_NAME)

# Analyze with AI
ai-cli chat "Prioritize and suggest fixes for these code issues: $ISSUES" --provider claude --max-tokens 3000
```

### Documentation Generation

```bash
# Generate docs for a project
ai-cli mcp search github "*.py" --owner myorg --repo myapi
ai-cli chat "Generate API documentation based on these Python files" --provider openai --model gpt-4
```

## 🔒 Security

- **Token Security**: Store sensitive tokens in environment variables
- **Minimal Permissions**: Use least-privilege access tokens
- **Local Processing**: Code analysis happens locally through MCP
- **No Data Storage**: Repository data isn't stored by the CLI

## 🧪 Development

### Setup Development Environment

```bash
# Clone and setup
git clone https://github.com/yourusername/ai-cli.git
cd ai-cli

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black ai_cli/
ruff check ai_cli/

# Type checking
mypy ai_cli/
```

### Project Structure

```
ai_cli/
├── cli/           # CLI interface and commands
├── providers/     # AI provider implementations
├── mcp/          # MCP client and servers
├── core/         # Configuration and utilities
└── utils/        # Helper functions

docs/             # Documentation
tests/            # Test suite
```

## 📋 Command Reference

### Global Options
```bash
ai-cli [OPTIONS] COMMAND [ARGS]...

Global Options:
  --config-dir PATH    Configuration directory path
  --verbose, -v        Enable verbose logging
  --help              Show help
```

### Core Commands

#### Chat Command
```bash
ai-cli chat MESSAGE [OPTIONS]

Arguments:
  MESSAGE               Message to send to AI [required]

Options:
  --provider, -p TEXT   AI provider (openai, claude, azure_openai, ollama)
  --model, -m TEXT      Model to use
  --stream, -s          Stream response
  --max-tokens INTEGER  Maximum tokens in response
  --temperature, -t FLOAT Temperature for generation (0.0-1.0)
```

#### Providers Command
```bash
ai-cli providers

# Lists all configured providers with their connection status and available models
```

#### Configuration Command
```bash
ai-cli config-cmd [OPTIONS]

Options:
  --show     Show current configuration
  --edit     Edit configuration file in default editor
  --init     Initialize new configuration with defaults
```

### MCP Commands

#### Connect to Services
```bash
ai-cli mcp connect SERVICE [OPTIONS]

Arguments:
  SERVICE              Service to connect to (gitlab, github)

Options:
  --token TEXT         Authentication token [required]
  --url TEXT           Base URL for service (optional)
```

#### Search Code
```bash
ai-cli mcp search SERVICE QUERY [OPTIONS]

Arguments:
  SERVICE              Service to search (gitlab, github)
  QUERY                Search query

Options:
  --owner TEXT         Repository owner
  --repo TEXT          Repository name
```

## 📚 Documentation

### 📋 [Complete Documentation Index](docs/index.md)
**Start here for comprehensive guides and navigation**

### Core Documentation
- **[📖 Installation Guide](docs/installation.md)** - Complete setup instructions for all providers
- **[📋 CLI Reference](docs/cli-reference.md)** - Complete command reference with syntax and examples
- **[🚀 Usage Guide](docs/usage.md)** - Workflows, best practices, and advanced usage patterns  
- **[🔌 MCP Integration](docs/mcp-integration.md)** - GitLab/GitHub integration for code context
- **[🏗️ Architecture Overview](docs/architecture.md)** - System design and scalability patterns

### Quick References
| Topic | Link | Description |
|-------|------|-------------|
| **Getting Started** | [Installation](docs/installation.md) | Setup AI CLI in 5 minutes |
| **All Commands** | [CLI Reference](docs/cli-reference.md) | Complete command syntax guide |
| **Basic Commands** | [Usage - Basic Commands](docs/usage.md#basic-commands) | Essential CLI operations |
| **Code Integration** | [MCP Integration](docs/mcp-integration.md) | Connect to GitLab/GitHub |
| **Advanced Workflows** | [Usage - Advanced Usage](docs/usage.md#advanced-usage) | Power user techniques |
| **Troubleshooting** | [Installation - Troubleshooting](docs/installation.md#troubleshooting) | Common issues and solutions |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for Claude and MCP protocol
- [OpenAI](https://openai.com) for GPT models
- [Ollama](https://ollama.ai) for local model support
- [Typer](https://typer.tiangolo.com) for the excellent CLI framework

## 📞 Support

- GitHub Issues: [Report bugs and request features](https://github.com/yourusername/ai-cli/issues)
- Documentation: [Full documentation](docs/)
- Examples: [Usage examples](docs/usage.md)

---

**AI CLI** - Bringing the power of multiple AI providers to your terminal with seamless code integration.