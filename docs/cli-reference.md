# CLI Command Reference

Complete reference for all AI CLI commands with examples and use cases.

## Global Commands

### Main Help
```bash
ai-cli --help
```
Shows the main help with all available commands and global options.

**Global Options:**
- `--config-dir PATH` - Specify custom configuration directory
- `--verbose, -v` - Enable verbose logging for debugging
- `--help` - Show help message

---

## Core Commands

### 1. Chat Command

Send messages to AI providers with full control over parameters.

#### Basic Syntax
```bash
ai-cli chat MESSAGE [OPTIONS]
```

#### Arguments
- `MESSAGE` - The message to send to the AI provider (required)

#### Options
- `--provider, -p TEXT` - AI provider: `openai`, `claude`, `azure_openai`, `ollama`
- `--model, -m TEXT` - Specific model to use (overrides config default)
- `--stream, -s` - Stream response in real-time
- `--max-tokens INTEGER` - Maximum tokens in response
- `--temperature, -t FLOAT` - Temperature for generation (0.0-1.0)

#### Examples

**Basic Chat:**
```bash
ai-cli chat "What is Python?"
```

**Provider-Specific Chat:**
```bash
ai-cli chat "Explain async programming" --provider claude
```

**Streaming with Parameters:**
```bash
ai-cli chat "Write a tutorial on Docker" --stream --max-tokens 2000 --temperature 0.7
```

**Model-Specific Chat:**
```bash
ai-cli chat "Code review this function" --provider openai --model gpt-4-turbo
```

#### Help
```bash
ai-cli chat --help
```

---

### 2. Providers Command

List all configured AI providers with their status and available models.

#### Basic Syntax
```bash
ai-cli providers
```

#### Output Information
- **Provider Name** - The configured provider identifier
- **Status** - Connection status (Connected/Disconnected/Error)
- **Models** - Available models for the provider

#### Example Output
```
                             Available AI Providers                             
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Provider     ┃ Status                        ┃ Models                        ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ openai       │ ✓ Connected                   │ gpt-4, gpt-4-turbo, gpt-3.5  │
│ claude       │ ✓ Connected                   │ claude-3-opus, claude-3-son.  │
│ ollama       │ ✗ Disconnected                │ llama2, llama2:13b (+6 more)  │
│ azure_openai │ ✗ Error: API key required     │ N/A                           │
└──────────────┴───────────────────────────────┴───────────────────────────────┘
```

#### Use Cases
- Check provider connection status
- Verify API key configuration
- See available models for each provider
- Troubleshoot connection issues

---

### 3. Configuration Command

Manage the AI CLI configuration file and settings.

#### Basic Syntax
```bash
ai-cli config-cmd [OPTIONS]
```

#### Options
- `--show` - Display current configuration
- `--edit` - Open configuration file in default editor
- `--init` - Initialize new configuration with defaults

#### Examples

**Initialize Configuration:**
```bash
ai-cli config-cmd --init
```
Creates `~/.config/ai-cli/config.yaml` with default settings.

**Show Current Configuration:**
```bash
ai-cli config-cmd --show
```
Displays configuration summary in a formatted panel.

**Edit Configuration:**
```bash
ai-cli config-cmd --edit
```
Opens the configuration file in your default editor.

#### Configuration File Location
- **Default:** `~/.config/ai-cli/config.yaml`
- **Custom:** Use `--config-dir` global option

#### Sample Configuration
```yaml
providers:
  openai:
    api_key: "sk-your-openai-key"
    model: "gpt-4"
    max_tokens: 4000
    temperature: 0.7
  
  claude:
    api_key: "sk-ant-your-claude-key"
    model: "claude-3-sonnet-20240229"

mcp:
  gitlab:
    auth_token: "glpat-your-gitlab-token"
  github:
    auth_token: "ghp_your-github-token"

default_provider: "openai"
log_level: "INFO"
```

---

## MCP Commands

### 1. MCP Connect Command

Connect to GitLab or GitHub repositories using authentication tokens.

#### Basic Syntax
```bash
ai-cli mcp connect SERVICE [OPTIONS]
```

#### Arguments
- `SERVICE` - Service to connect to: `gitlab` or `github`

#### Options
- `--token TEXT` - Authentication token (required)
- `--url TEXT` - Base URL for service (optional, uses defaults)

#### Examples

**Connect to GitHub:**
```bash
ai-cli mcp connect github --token ghp_your_github_token
```

**Connect to GitLab:**
```bash
ai-cli mcp connect gitlab --token glpat_your_gitlab_token
```

**Connect to Self-Hosted GitLab:**
```bash
ai-cli mcp connect gitlab --token glpat_token --url https://gitlab.company.com
```

#### Token Requirements

**GitHub Personal Access Token:**
- Scopes: `repo`, `read:org`, `user:email`
- Generate at: GitHub → Settings → Developer settings → Personal access tokens

**GitLab Personal Access Token:**
- Scopes: `api`, `read_repository`, `read_user`
- Generate at: GitLab → User Settings → Access Tokens

#### Output
```bash
✓ Successfully connected to github
Available resources: 15
```

---

### 2. MCP Search Command

Search code across connected GitLab or GitHub repositories.

#### Basic Syntax
```bash
ai-cli mcp search SERVICE QUERY [OPTIONS]
```

#### Arguments
- `SERVICE` - Service to search: `gitlab` or `github`
- `QUERY` - Search query string

#### Options
- `--owner TEXT` - Repository owner/organization
- `--repo TEXT` - Specific repository name

#### Examples

**Global Search:**
```bash
ai-cli mcp search github "authentication middleware"
```

**Organization-Specific Search:**
```bash
ai-cli mcp search github "function login" --owner myorg
```

**Repository-Specific Search:**
```bash
ai-cli mcp search gitlab "TODO|FIXME" --owner myteam --repo backend
```

**Complex Query:**
```bash
ai-cli mcp search github "class.*Controller" --owner myorg --repo webapp
```

#### Output Format
```
                          Search Results from github                           
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Repository        ┃ File              ┃ Line    ┃ Preview                       ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ myorg/webapp      │ auth.py           │ 45      │ def authenticate_user(token): │
│ myorg/backend     │ middleware.py     │ 12      │ class AuthMiddleware:         │
└───────────────────┴───────────────────┴─────────┴───────────────────────────────┘
```

#### Search Query Tips
- Use quotes for exact phrases: `"function main"`
- Use regex patterns: `class.*Controller`
- Use logical operators: `TODO|FIXME|HACK`
- Use file extensions: `*.py` (GitHub only)
- Use language filters: `language:python` (GitHub only)

---

## Advanced Usage Patterns

### 1. Combining Chat with MCP

**Code Review Workflow:**
```bash
# 1. Search for recent changes
ai-cli mcp search github "authentication" --owner myorg --repo webapp

# 2. Copy relevant file paths from search results
# 3. Analyze with AI
ai-cli chat "Review this authentication code for security vulnerabilities" --provider claude
```

**Documentation Generation:**
```bash
# 1. Find project structure
ai-cli mcp search github "README|main.py|__init__.py" --owner myorg --repo project

# 2. Generate docs
ai-cli chat "Create API documentation based on these Python files" --provider openai --max-tokens 3000
```

### 2. Multi-Provider Comparison

```bash
# Compare responses from different providers
ai-cli chat "Explain microservices architecture" --provider openai > openai_response.txt
ai-cli chat "Explain microservices architecture" --provider claude > claude_response.txt
ai-cli chat "Explain microservices architecture" --provider ollama > ollama_response.txt
```

### 3. Streaming for Long Content

```bash
# Stream long responses to see progress
ai-cli chat "Write a comprehensive tutorial on Kubernetes deployment" --stream --provider claude --max-tokens 4000
```

### 4. Configuration Profiles

```bash
# Development environment
export AI_CLI_CONFIG_DIR="~/.config/ai-cli-dev"
ai-cli config-cmd --init

# Production environment  
export AI_CLI_CONFIG_DIR="~/.config/ai-cli-prod"
ai-cli config-cmd --init
```

---

## Error Handling and Troubleshooting

### Common Error Messages

**"API key is required"**
```bash
# Solution: Add API key to configuration
ai-cli config-cmd --edit
# Or set environment variable
export AI_CLI_OPENAI_API_KEY="sk-your-key"
```

**"MCP not available"**
```bash
# Solution: Install MCP dependencies (optional)
pip install mcp fastmcp
```

**"Connection failed"**
```bash
# Solution: Check token permissions and network
ai-cli config-cmd --show
curl -H "Authorization: Bearer token" https://api.github.com/user
```

### Debugging Commands

**Verbose Logging:**
```bash
ai-cli --verbose chat "test message"
ai-cli --verbose mcp connect github --token token
```

**Configuration Check:**
```bash
ai-cli config-cmd --show
ai-cli providers
```

**Help for Any Command:**
```bash
ai-cli --help
ai-cli chat --help
ai-cli mcp --help
ai-cli mcp connect --help
ai-cli mcp search --help
```

---

## Environment Variables

Override any configuration option using environment variables with the `AI_CLI_` prefix:

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

This allows for flexible deployment across different environments without modifying configuration files.