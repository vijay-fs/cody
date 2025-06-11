# Installation Guide

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Git (for development)

## Installation Methods

### 1. From Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-cli.git
cd ai-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Install development dependencies (optional)
pip install -e ".[dev]"
```

### 2. From PyPI (Future Release)

```bash
pip install ai-cli
```

## Configuration

### Initial Setup

1. Initialize configuration:
```bash
ai-cli config-cmd --init
```

2. Edit configuration file:
```bash
ai-cli config-cmd --edit
```

Or manually edit `~/.config/ai-cli/config.yaml`

### Provider Configuration

#### OpenAI

```yaml
providers:
  openai:
    api_key: "sk-your-openai-key-here"
    model: "gpt-4"
    max_tokens: 4000
    temperature: 0.7
```

Set via environment variable:
```bash
export AI_CLI_OPENAI_API_KEY="sk-your-openai-key-here"
```

#### Claude (Anthropic)

```yaml
providers:
  claude:
    api_key: "sk-ant-your-claude-key-here"
    model: "claude-3-sonnet-20240229"
    max_tokens: 4000
    temperature: 0.7
```

Set via environment variable:
```bash
export AI_CLI_CLAUDE_API_KEY="sk-ant-your-claude-key-here"
```

#### Azure OpenAI

```yaml
providers:
  azure_openai:
    endpoint: "https://your-resource.openai.azure.com/"
    api_key: "your-azure-api-key"
    deployment_name: "gpt-4"
    api_version: "2024-02-01"
    max_tokens: 4000
    temperature: 0.7
```

#### Ollama

```yaml
providers:
  ollama:
    base_url: "http://localhost:11434"
    model: "llama2"
    max_tokens: 4000
    temperature: 0.7
```

Make sure Ollama is running locally:
```bash
ollama serve  # Start Ollama server
ollama pull llama2  # Download model
```

### MCP Configuration

#### GitLab

1. Generate a personal access token in GitLab:
   - Go to GitLab → Settings → Access Tokens
   - Create token with `api` scope

2. Configure:
```yaml
mcp:
  gitlab:
    auth_token: "glpat-your-gitlab-token"
    base_url: "https://gitlab.com"  # or your GitLab instance URL
```

#### GitHub

1. Generate a personal access token in GitHub:
   - Go to GitHub → Settings → Developer settings → Personal access tokens
   - Create token with `repo` and `read:org` scopes

2. Configure:
```yaml
mcp:
  github:
    auth_token: "ghp_your-github-token"
    base_url: "https://api.github.com"
```

## Verification

### Test AI Providers

```bash
# List available providers
ai-cli providers

# Test OpenAI
ai-cli chat "Hello, world!" --provider openai

# Test Claude
ai-cli chat "Hello, world!" --provider claude

# Test streaming
ai-cli chat "Write a short poem" --provider openai --stream
```

### Test MCP Integration

```bash
# Connect to GitLab
ai-cli mcp connect gitlab --token glpat-your-token

# Connect to GitHub
ai-cli mcp connect github --token ghp_your-token

# Search code
ai-cli mcp search github "function main" --owner yourusername --repo yourrepo
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate
   
   # Reinstall dependencies
   pip install -e .
   ```

2. **API Key Errors**
   ```bash
   # Check configuration
   ai-cli config-cmd --show
   
   # Test provider connection
   ai-cli providers
   ```

3. **MCP Connection Issues**
   - Verify token permissions
   - Check network connectivity
   - Ensure correct base URLs

4. **Ollama Connection Issues**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Start Ollama if not running
   ollama serve
   ```

### Logging

Enable verbose logging for debugging:

```bash
ai-cli --verbose chat "test message"
```

Or set log level in config:
```yaml
log_level: "DEBUG"
```

## Environment Variables

All configuration options can be overridden with environment variables:

```bash
# Provider settings
export AI_CLI_DEFAULT_PROVIDER="claude"
export AI_CLI_OPENAI_API_KEY="sk-..."
export AI_CLI_CLAUDE_API_KEY="sk-ant-..."

# MCP settings
export AI_CLI_GITLAB_AUTH_TOKEN="glpat-..."
export AI_CLI_GITHUB_AUTH_TOKEN="ghp_..."

# General settings
export AI_CLI_CONFIG_DIR="/custom/config/path"
export AI_CLI_LOG_LEVEL="DEBUG"
```

## Updating

### From Source
```bash
cd ai-cli
git pull origin main
pip install -e .
```

### From PyPI (Future)
```bash
pip install --upgrade ai-cli
```