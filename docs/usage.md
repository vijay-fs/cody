# Usage Guide

## Basic Commands

### Chat with AI Providers

Send messages to AI providers:

```bash
# Basic chat
ai-cli chat "Explain quantum computing"

# Specify provider
ai-cli chat "Write a Python function" --provider claude

# Specify model
ai-cli chat "Help me debug this code" --provider openai --model gpt-4-turbo

# Stream response
ai-cli chat "Write a long story" --stream

# Adjust parameters
ai-cli chat "Be creative" --temperature 0.9 --max-tokens 1000
```

### Provider Management

```bash
# List all providers and their status
ai-cli providers

# Check current configuration
ai-cli config-cmd --show

# Edit configuration
ai-cli config-cmd --edit

# Initialize new configuration
ai-cli config-cmd --init
```

### MCP Integration

#### Connecting to Services

```bash
# Connect to GitLab
ai-cli mcp connect gitlab --token glpat-xxxxxxxxxxxx

# Connect to GitHub
ai-cli mcp connect github --token ghp_xxxxxxxxxxxx

# Connect with custom URL
ai-cli mcp connect gitlab --token glpat-xxx --url https://gitlab.company.com
```

#### Searching Code

```bash
# Search across all accessible repositories
ai-cli mcp search github "function authenticate"

# Search in specific repository
ai-cli mcp search github "class UserModel" --owner myorg --repo myproject

# Search in GitLab
ai-cli mcp search gitlab "TODO" --owner myteam --repo backend
```

## Advanced Usage

### Multi-Provider Workflows

Compare responses from different providers:

```bash
# Get responses from multiple providers
ai-cli chat "Explain this algorithm" --provider openai > openai_response.txt
ai-cli chat "Explain this algorithm" --provider claude > claude_response.txt
ai-cli chat "Explain this algorithm" --provider ollama > ollama_response.txt
```

### Code Analysis with MCP

Combine AI providers with code context:

```bash
# First, search for relevant code
ai-cli mcp search github "authentication middleware" --owner myorg --repo webapp

# Then analyze with AI (copy relevant file paths from search results)
ai-cli chat "Analyze this authentication middleware for security issues" --provider claude
```

### Scripting and Automation

Use in shell scripts:

```bash
#!/bin/bash

# Automated code review
REPO_OWNER="myorg"
REPO_NAME="myproject"

# Search for potential issues
RESULTS=$(ai-cli mcp search github "TODO|FIXME|HACK" --owner $REPO_OWNER --repo $REPO_NAME)

if [ ! -z "$RESULTS" ]; then
    echo "Found potential issues:"
    echo "$RESULTS"
    
    # Get AI analysis
    ai-cli chat "Review these code issues and suggest fixes: $RESULTS" --provider claude
fi
```

### Configuration Profiles

Create different configurations for different environments:

```bash
# Development environment
export AI_CLI_CONFIG_DIR="~/.config/ai-cli-dev"
ai-cli config --init
# Configure with development API keys

# Production environment
export AI_CLI_CONFIG_DIR="~/.config/ai-cli-prod"
ai-cli config --init
# Configure with production API keys
```

## Command Reference

### Global Options

```bash
ai-cli [GLOBAL-OPTIONS] COMMAND [COMMAND-OPTIONS]

Global Options:
  --config-dir PATH    Configuration directory
  --verbose, -v        Enable verbose logging
  --help              Show help
```

### Chat Command

```bash
ai-cli chat MESSAGE [OPTIONS]

Options:
  --provider, -p TEXT        AI provider (openai, claude, azure_openai, ollama)
  --model, -m TEXT          Model to use
  --stream, -s              Stream response
  --max-tokens INTEGER      Maximum tokens in response
  --temperature, -t FLOAT   Temperature for generation (0.0-1.0)
```

### Providers Command

```bash
ai-cli providers

Shows status of all configured providers
```

### Config Command

```bash
ai-cli config-cmd [OPTIONS]

Options:
  --show     Show current configuration
  --edit     Edit configuration file
  --init     Initialize new configuration
```

### MCP Commands

```bash
ai-cli mcp SUBCOMMAND [OPTIONS]

Subcommands:
  connect    Connect to MCP service
  search     Search code in connected services
```

#### MCP Connect

```bash
ai-cli mcp connect SERVICE [OPTIONS]

Arguments:
  SERVICE    Service to connect to (gitlab, github)

Options:
  --token TEXT    Authentication token
  --url TEXT      Base URL for service
```

#### MCP Search

```bash
ai-cli mcp search SERVICE QUERY [OPTIONS]

Arguments:
  SERVICE    Service to search (gitlab, github)
  QUERY      Search query

Options:
  --owner TEXT    Repository owner
  --repo TEXT     Repository name
```

## Examples

### Code Review Workflow

```bash
# 1. Search for recent changes
ai-cli mcp search github "function.*user.*login" --owner myteam --repo backend

# 2. Analyze security implications
ai-cli chat "Review this login function for security vulnerabilities" --provider claude

# 3. Get suggestions for improvements
ai-cli chat "Suggest improvements for this authentication code" --provider openai --model gpt-4
```

### Documentation Generation

```bash
# Generate documentation for a function
ai-cli chat "Generate comprehensive documentation for this Python function: $(cat myfunction.py)" --provider claude --max-tokens 2000

# Create README for a project
ai-cli mcp search github "README" --owner myorg --repo myproject
ai-cli chat "Create a README.md for this project based on the codebase structure" --provider openai
```

### Code Refactoring

```bash
# Get refactoring suggestions
ai-cli chat "Refactor this legacy code to modern Python practices: $(cat legacy_code.py)" --provider claude --temperature 0.3

# Generate unit tests
ai-cli chat "Generate comprehensive unit tests for this function" --provider openai --model gpt-4
```

### Learning and Exploration

```bash
# Understand new codebases
ai-cli mcp search github "main.py|__init__.py" --owner opensourceorg --repo interestingproject
ai-cli chat "Explain the architecture of this project based on the main files" --provider claude

# Learn from examples
ai-cli mcp search github "machine learning" --owner scikit-learn --repo scikit-learn
ai-cli chat "Explain how this machine learning implementation works" --provider openai
```

## Tips and Best Practices

### 1. Provider Selection

- **OpenAI GPT-4**: Best for complex reasoning and code analysis
- **Claude**: Excellent for long-form content and detailed explanations
- **Ollama**: Good for privacy-sensitive tasks and offline usage
- **Azure OpenAI**: Enterprise-grade with compliance features

### 2. Temperature Settings

- **0.0-0.3**: Deterministic, good for code and factual content
- **0.4-0.7**: Balanced creativity and accuracy
- **0.8-1.0**: High creativity, good for brainstorming

### 3. Token Management

- Use `--max-tokens` to control response length
- Monitor usage with provider dashboards
- Consider costs for different providers

### 4. Security

- Never commit API keys to version control
- Use environment variables for sensitive configuration
- Regularly rotate authentication tokens
- Review MCP permissions and scopes

### 5. Performance

- Use streaming (`--stream`) for long responses
- Cache frequent queries when possible
- Consider local models (Ollama) for repeated tasks