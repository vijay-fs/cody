# MCP Integration Guide

## Model Context Protocol (MCP) Overview

The Model Context Protocol (MCP) enables AI applications to securely access external data sources and tools. Our CLI integrates with MCP to provide seamless access to GitLab and GitHub repositories, allowing AI providers to understand and work with your codebase context.

## Supported Services

### GitLab Integration

- **Repository Access**: Browse projects, files, and directories
- **Code Search**: Search across repositories and files
- **File Content**: Retrieve file contents with syntax highlighting context
- **Commit History**: Access commit logs and changes
- **Project Information**: Get repository metadata and statistics

### GitHub Integration

- **Repository Access**: List and browse repositories
- **Code Search**: Advanced code search across repositories
- **File Operations**: Read file contents and directory structures
- **Commit History**: Access commit logs and diffs
- **Repository Search**: Find repositories by various criteria

## Authentication Setup

### GitLab Personal Access Token

1. **Generate Token**:
   - Navigate to GitLab → User Settings → Access Tokens
   - Create a new token with the following scopes:
     - `api` - Full API access
     - `read_repository` - Read repository contents
     - `read_user` - Read user information

2. **Configure CLI**:
   ```bash
   # Via configuration file
   ai-cli config-cmd --edit
   
   # Add to config.yaml:
   mcp:
     gitlab:
       auth_token: "glpat-your-token-here"
       base_url: "https://gitlab.com"  # or your instance URL
   
   # Or via environment variable
   export AI_CLI_GITLAB_AUTH_TOKEN="glpat-your-token-here"
   ```

3. **Test Connection**:
   ```bash
   ai-cli mcp connect gitlab --token glpat-your-token-here
   ```

### GitHub Personal Access Token

1. **Generate Token**:
   - Navigate to GitHub → Settings → Developer settings → Personal access tokens
   - Create a new token with the following scopes:
     - `repo` - Full repository access
     - `read:org` - Read organization membership
     - `user:email` - Read user email

2. **Configure CLI**:
   ```bash
   # Via configuration file
   ai-cli config-cmd --edit
   
   # Add to config.yaml:
   mcp:
     github:
       auth_token: "ghp_your-token-here"
       base_url: "https://api.github.com"
   
   # Or via environment variable
   export AI_CLI_GITHUB_AUTH_TOKEN="ghp_your-token-here"
   ```

3. **Test Connection**:
   ```bash
   ai-cli mcp connect github --token ghp_your-token-here
   ```

## Usage Examples

### Basic Repository Exploration

```bash
# List your repositories
ai-cli mcp connect github --token your-token
ai-cli chat "What repositories do I have access to?" --provider claude

# Explore a specific repository structure
ai-cli mcp search github "package.json|requirements.txt|Cargo.toml" --owner myorg --repo myproject
ai-cli chat "Analyze the project structure and dependencies" --provider openai
```

### Code Analysis and Review

```bash
# Search for security-related code
ai-cli mcp search gitlab "password|secret|token" --owner myteam --repo backend
ai-cli chat "Review these security-related code snippets for potential vulnerabilities" --provider claude

# Find and analyze specific patterns
ai-cli mcp search github "class.*Controller" --owner myorg --repo webapp
ai-cli chat "Analyze these controller classes for best practices and potential improvements" --provider openai
```

### Documentation and Learning

```bash
# Understand project architecture
ai-cli mcp search github "main.py|index.js|app.py" --owner opensource --repo project
ai-cli chat "Explain the main entry points and overall architecture of this project" --provider claude

# Generate documentation
ai-cli mcp search gitlab "src/.*\.py" --owner myteam --repo api
ai-cli chat "Generate API documentation based on these Python source files" --provider openai --max-tokens 3000
```

### Bug Hunting and Debugging

```bash
# Search for TODO and FIXME comments
ai-cli mcp search github "TODO|FIXME|HACK|XXX" --owner myorg --repo myproject
ai-cli chat "Prioritize these technical debt items and suggest solutions" --provider claude

# Find error handling patterns
ai-cli mcp search gitlab "try.*except|catch.*error" --owner myteam --repo service
ai-cli chat "Review error handling patterns and suggest improvements" --provider openai
```

## Advanced Integration Patterns

### Multi-Repository Analysis

```bash
#!/bin/bash

# Analyze multiple repositories for consistency
REPOS=("frontend" "backend" "mobile")
ORG="myorg"

for repo in "${REPOS[@]}"; do
    echo "Analyzing $repo..."
    
    # Search for configuration files
    CONFIG_FILES=$(ai-cli mcp search github "config|settings" --owner $ORG --repo $repo)
    
    # Get AI analysis
    ai-cli chat "Analyze configuration consistency across repositories: $CONFIG_FILES" --provider claude
done
```

### Code Migration and Refactoring

```bash
# Find deprecated patterns
ai-cli mcp search github "deprecated|legacy|old" --owner myorg --repo codebase
ai-cli chat "Create a migration plan for these deprecated code patterns" --provider openai --model gpt-4

# Identify modernization opportunities
ai-cli mcp search gitlab "python2|jQuery|var " --owner myteam --repo webapp
ai-cli chat "Suggest modernization strategies for this legacy code" --provider claude
```

### Onboarding and Knowledge Transfer

```bash
# Create developer onboarding guide
ai-cli mcp search github "README|CONTRIBUTING|docs/" --owner myorg --repo project
ai-cli chat "Create a comprehensive developer onboarding guide based on existing documentation" --provider claude --max-tokens 4000

# Generate architecture overview
ai-cli mcp search gitlab "src/|lib/|components/" --owner myteam --repo application
ai-cli chat "Create an architecture diagram description based on the codebase structure" --provider openai
```

## MCP Server Architecture

### Custom MCP Servers

The CLI includes custom MCP servers for GitLab and GitHub:

```python
# GitLab MCP Server
ai_cli/mcp/gitlab_server.py

# GitHub MCP Server  
ai_cli/mcp/github_server.py
```

### Available Resources

#### GitLab Resources

- `gitlab://projects` - List accessible projects
- `gitlab://{owner}/{repo}/files` - Repository file tree
- `gitlab://{owner}/{repo}/file/{path}` - Specific file content

#### GitHub Resources

- `github://user/repos` - User repositories
- `github://{owner}/{repo}/contents` - Repository contents
- `github://{owner}/{repo}/file/{path}` - Specific file content

### Available Tools

#### GitLab Tools

- `search_code` - Search code across repositories
- `get_file_content` - Retrieve file contents
- `list_commits` - Get commit history

#### GitHub Tools

- `search_code` - Advanced code search
- `get_file_content` - Retrieve file contents
- `list_commits` - Get commit history
- `search_repositories` - Find repositories
- `get_repository_info` - Repository metadata

## Security and Privacy

### Token Security

- **Scope Limitation**: Use minimal required scopes for tokens
- **Regular Rotation**: Rotate tokens periodically
- **Environment Variables**: Store tokens in environment variables, not config files
- **Access Logging**: Monitor token usage in provider dashboards

### Data Privacy

- **Local Processing**: MCP integration processes data locally
- **No Data Storage**: CLI doesn't store repository data
- **Controlled Access**: Only requested data is sent to AI providers
- **Audit Trail**: All API calls are logged for review

### Best Practices

1. **Principle of Least Privilege**: Grant minimal necessary permissions
2. **Regular Audits**: Review token permissions and usage
3. **Secure Configuration**: Use environment variables for sensitive data
4. **Access Control**: Limit repository access to necessary projects
5. **Monitoring**: Set up alerts for unusual API usage

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   ```bash
   # Check token validity
   curl -H "Authorization: Bearer your-token" https://api.github.com/user
   
   # Verify scopes
   ai-cli config-cmd --show
   ```

2. **Network Connectivity**:
   ```bash
   # Test API endpoint
   curl https://api.github.com/
   curl https://gitlab.com/api/v4/version
   ```

3. **Permission Errors**:
   - Verify repository access permissions
   - Check organization membership
   - Ensure token hasn't expired

### Debugging

Enable verbose logging:

```bash
ai-cli --verbose mcp connect github --token your-token
```

Check MCP server logs:

```bash
# GitLab server logs
python -m ai_cli.mcp.gitlab_server

# GitHub server logs  
python -m ai_cli.mcp.github_server
```

## Integration Examples

### Automated Code Review

```python
#!/usr/bin/env python3
import subprocess
import json

def review_pull_request(owner, repo, pr_number):
    # Get PR files
    files_cmd = f"ai-cli mcp search github 'pull request {pr_number}' --owner {owner} --repo {repo}"
    files_result = subprocess.run(files_cmd.split(), capture_output=True, text=True)
    
    # AI review
    review_cmd = f"ai-cli chat 'Review this pull request for code quality and security: {files_result.stdout}' --provider claude"
    review_result = subprocess.run(review_cmd.split(), capture_output=True, text=True)
    
    return review_result.stdout

# Usage
review = review_pull_request("myorg", "myrepo", 123)
print(review)
```

### Documentation Generator

```bash
#!/bin/bash

# Generate project documentation
PROJECT_OWNER="myorg"
PROJECT_REPO="myproject"

# Get project structure
STRUCTURE=$(ai-cli mcp search github "README|src/|lib/|docs/" --owner $PROJECT_OWNER --repo $PROJECT_REPO)

# Generate documentation
ai-cli chat "Generate comprehensive project documentation based on this structure: $STRUCTURE" --provider claude --max-tokens 4000 > project_docs.md

echo "Documentation generated: project_docs.md"
```

This MCP integration enables powerful workflows that combine the contextual understanding of your codebase with the analytical capabilities of modern AI providers.