# AI CLI Tool Architecture

## Overview
A scalable CLI tool that provides unified access to multiple AI providers with MCP integration for source code access from GitLab and GitHub.

## Architecture Design

### Core Components

#### 1. CLI Layer (`cli/`)
- **Main CLI Interface**: Entry point using Typer for modern, type-safe CLI
- **Command Router**: Routes commands to appropriate handlers
- **Configuration Manager**: Handles provider configs, auth tokens, and user settings

#### 2. AI Provider Layer (`providers/`)
- **Abstract Provider Interface**: Common interface for all AI providers
- **Provider Implementations**:
  - OpenAI Provider
  - Azure OpenAI Provider  
  - Claude (Anthropic) Provider
  - Ollama Provider
- **Provider Factory**: Dynamic provider instantiation
- **Response Normalizer**: Standardizes responses across providers

#### 3. MCP Integration Layer (`mcp/`)
- **MCP Client**: Core MCP protocol client implementation
- **GitLab MCP Server**: Connects to GitLab using auth tokens
- **GitHub MCP Server**: Connects to GitHub using auth tokens
- **Resource Managers**: Handle code repository access and file operations

#### 4. Core Services (`core/`)
- **Session Manager**: Handles conversation context and history
- **Authentication Manager**: Manages API keys and auth tokens
- **Configuration Service**: Centralized config management
- **Logging Service**: Structured logging and debugging

#### 5. Utilities (`utils/`)
- **HTTP Client**: Shared HTTP client with retry logic
- **Error Handling**: Standardized error types and handlers
- **Validation**: Input validation and sanitization
- **Formatters**: Output formatting for different content types

## Data Flow

```
CLI Command → Command Router → Provider Factory → AI Provider
                          ↓
            MCP Client → GitLab/GitHub → Source Code Context
                          ↓
            Response Normalizer → Output Formatter → User
```

## Technology Stack

### Core Technologies
- **Python 3.9+**: Main language
- **Typer**: Modern CLI framework with automatic help generation
- **Pydantic**: Data validation and settings management
- **httpx**: Async HTTP client for API calls
- **asyncio**: Async programming support

### AI Provider SDKs
- **openai**: Official OpenAI Python SDK
- **azure-openai**: Azure OpenAI integration
- **anthropic**: Claude API client
- **ollama**: Local Ollama integration

### MCP Integration
- **mcp**: Model Context Protocol Python SDK
- **FastMCP**: Server creation framework

## Configuration Structure

```yaml
# ~/.config/ai-cli/config.yaml
providers:
  openai:
    api_key: "sk-..."
    model: "gpt-4"
    max_tokens: 4000
  
  azure_openai:
    endpoint: "https://your-resource.openai.azure.com/"
    api_key: "..."
    deployment_name: "gpt-4"
  
  claude:
    api_key: "sk-ant-..."
    model: "claude-3-sonnet-20240229"
  
  ollama:
    base_url: "http://localhost:11434"
    model: "llama2"

mcp:
  gitlab:
    auth_token: "glpat-..."
    base_url: "https://gitlab.com"
  
  github:
    auth_token: "ghp_..."
    base_url: "https://api.github.com"

default_provider: "openai"
```

## Scalability Features

### Provider Extensibility
- Plugin-style architecture for adding new AI providers
- Abstract interfaces ensure consistent behavior
- Factory pattern for dynamic provider selection

### MCP Extensibility  
- Modular MCP server implementations
- Easy addition of new source code platforms
- Standardized resource and tool interfaces

### Configuration Management
- Environment-based configuration override
- Profile-based settings for different use cases
- Secure credential storage options

### Performance Optimizations
- Async operations throughout the stack
- Connection pooling for HTTP clients
- Caching for MCP resources and AI responses
- Streaming support for large responses

## Security Considerations

### Authentication
- Secure storage of API keys and tokens
- Environment variable override support
- Optional keyring integration for credential storage

### MCP Security
- Token-based authentication for GitLab/GitHub
- Scoped permissions for repository access
- Request validation and sanitization

### Network Security
- TLS/SSL for all external communications
- Request timeout and retry policies
- Rate limiting compliance

## Error Handling Strategy

### Hierarchical Error Types
- `AIProviderError`: Base for provider-specific errors
- `MCPError`: MCP protocol and connection errors  
- `ConfigurationError`: Configuration and setup errors
- `ValidationError`: Input validation failures

### Resilience Patterns
- Automatic retry with exponential backoff
- Graceful degradation when services unavailable
- Fallback provider selection
- Comprehensive error logging and reporting