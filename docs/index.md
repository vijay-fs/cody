# AI CLI Documentation

Welcome to the AI CLI documentation! This comprehensive guide will help you get started with the scalable command-line tool for multiple AI providers with MCP integration.

## 📖 Documentation Overview

### Getting Started
- **[Installation Guide](installation.md)** - Step-by-step setup instructions for all platforms and providers
- **[CLI Reference](cli-reference.md)** - Complete command reference with examples and syntax
- **[Usage Guide](usage.md)** - Workflows, best practices, and advanced usage patterns

### Advanced Features
- **[MCP Integration](mcp-integration.md)** - GitLab and GitHub integration for code context
- **[Architecture Overview](architecture.md)** - System design, scalability, and extensibility

## 🚀 Quick Navigation

### For New Users
1. **Start Here**: [Installation Guide](installation.md)
2. **Command Reference**: [CLI Reference](cli-reference.md)
3. **Basic Usage**: [Usage Guide - Basic Commands](usage.md#basic-commands)
4. **Configuration**: [Usage Guide - Provider Management](usage.md#provider-management)

### For Developers
1. **Code Integration**: [MCP Integration Guide](mcp-integration.md)
2. **Advanced Workflows**: [Usage Guide - Advanced Usage](usage.md#advanced-usage)
3. **Architecture**: [Architecture Overview](architecture.md)

### For System Administrators
1. **Security**: [MCP Integration - Security](mcp-integration.md#security-and-privacy)
2. **Configuration Management**: [Installation Guide - Configuration](installation.md#configuration)
3. **Troubleshooting**: [Installation Guide - Troubleshooting](installation.md#troubleshooting)

## 🎯 Key Features Covered

### AI Provider Support
- **OpenAI GPT Models** - Complete integration with streaming support
- **Claude (Anthropic)** - Advanced reasoning and long-form content
- **Azure OpenAI** - Enterprise deployment with custom endpoints
- **Ollama** - Local models for privacy and offline usage

### MCP Integration
- **GitLab Integration** - Repository access, code search, file operations
- **GitHub Integration** - Advanced code search, repository management
- **Security Features** - Token-based authentication, scoped permissions

### CLI Features
- **Rich Terminal Interface** - Beautiful output with syntax highlighting
- **Streaming Responses** - Real-time output for long responses
- **Flexible Configuration** - YAML config with environment overrides
- **Extensible Architecture** - Plugin-style provider system

## 📋 Command Quick Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `ai-cli chat` | Send messages to AI providers | `ai-cli chat "Explain Python" --provider claude` |
| `ai-cli providers` | List provider status | `ai-cli providers` |
| `ai-cli config-cmd` | Manage configuration | `ai-cli config-cmd --show` |
| `ai-cli mcp connect` | Connect to repositories | `ai-cli mcp connect github --token TOKEN` |
| `ai-cli mcp search` | Search code | `ai-cli mcp search github "function main"` |

## 🔧 Configuration Files

### Main Configuration
- **Location**: `~/.config/ai-cli/config.yaml`
- **Purpose**: Provider settings, API keys, default options
- **Documentation**: [Installation Guide - Configuration](installation.md#configuration)

### Environment Variables
- **Purpose**: Override configuration, secure credential storage
- **Examples**: `AI_CLI_OPENAI_API_KEY`, `AI_CLI_DEFAULT_PROVIDER`
- **Documentation**: [Installation Guide - Environment Variables](installation.md#environment-variables)

## 🔒 Security Considerations

### API Key Management
- Store sensitive keys in environment variables
- Use minimal required token scopes
- Regular key rotation best practices

### MCP Security
- Token-based authentication for GitLab/GitHub
- Scoped repository access permissions
- Local processing with controlled data flow

**Full Security Guide**: [MCP Integration - Security](mcp-integration.md#security-and-privacy)

## 🛠️ Troubleshooting

### Common Issues
1. **Installation Problems** - [Installation Guide - Troubleshooting](installation.md#troubleshooting)
2. **Provider Connection Issues** - [Usage Guide - Tips and Best Practices](usage.md#tips-and-best-practices)
3. **MCP Authentication** - [MCP Integration - Troubleshooting](mcp-integration.md#troubleshooting)

### Getting Help
- **Command Help**: Use `--help` with any command
- **Verbose Logging**: Add `--verbose` flag for debugging
- **Configuration Check**: Run `ai-cli config-cmd --show`

## 🚀 Example Workflows

### Code Review Workflow
```bash
# 1. Connect to repository
ai-cli mcp connect github --token YOUR_TOKEN

# 2. Search for recent changes
ai-cli mcp search github "function.*login" --owner myorg --repo webapp

# 3. Analyze with AI
ai-cli chat "Review this login function for security issues" --provider claude
```

### Documentation Generation
```bash
# 1. Search project structure
ai-cli mcp search github "README|main.py|__init__.py" --owner myorg --repo project

# 2. Generate documentation
ai-cli chat "Create API documentation based on these files" --provider openai --max-tokens 3000
```

### Multi-Provider Analysis
```bash
# Compare responses from different providers
ai-cli chat "Explain microservices architecture" --provider openai > openai_response.txt
ai-cli chat "Explain microservices architecture" --provider claude > claude_response.txt
```

## 📚 External Resources

### API Documentation
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic Claude API](https://docs.anthropic.com/claude/reference)
- [Azure OpenAI Service](https://docs.microsoft.com/azure/cognitive-services/openai/)
- [Ollama Documentation](https://ollama.ai/docs)

### MCP Protocol
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

### Development Tools
- [Typer CLI Framework](https://typer.tiangolo.com/)
- [Rich Terminal Library](https://rich.readthedocs.io/)
- [Pydantic Validation](https://docs.pydantic.dev/)

---

**Need Help?** Start with the [Installation Guide](installation.md) or jump to specific topics using the navigation above.