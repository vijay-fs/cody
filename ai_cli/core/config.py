from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings
import yaml
import os


class ProviderConfig(BaseSettings):
    api_key: Optional[str] = None
    model: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7


class OpenAIConfig(ProviderConfig):
    model: str = "gpt-4"
    api_key: Optional[str] = None


class AzureOpenAIConfig(ProviderConfig):
    endpoint: Optional[str] = None
    deployment_name: Optional[str] = None
    api_version: str = "2024-02-01"


class ClaudeConfig(ProviderConfig):
    model: str = "claude-3-sonnet-20240229"
    api_key: Optional[str] = None


class OllamaConfig(ProviderConfig):
    base_url: str = "http://localhost:11434"
    model: str = "llama2"


class MCPGitLabConfig(BaseSettings):
    auth_token: Optional[str] = None
    base_url: str = "https://gitlab.com"


class MCPGitHubConfig(BaseSettings):
    auth_token: Optional[str] = None
    base_url: str = "https://api.github.com"


class MCPConfig(BaseSettings):
    gitlab: MCPGitLabConfig = MCPGitLabConfig()
    github: MCPGitHubConfig = MCPGitHubConfig()


class AICliConfig(BaseSettings):
    providers: Dict[str, Dict[str, Any]] = {
        "openai": {},
        "azure_openai": {},
        "claude": {},
        "ollama": {}
    }
    mcp: Dict[str, Dict[str, Any]] = {
        "gitlab": {},
        "github": {}
    }
    default_provider: str = "openai"
    config_dir: Path = Path.home() / ".config" / "ai-cli"
    log_level: str = "INFO"
    
    class Config:
        env_prefix = "AI_CLI_"
        
    @field_validator('config_dir', mode='before')
    @classmethod
    def ensure_path(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v

    def load_config_file(self) -> None:
        config_file = self.config_dir / "config.yaml"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
                if config_data:
                    for key, value in config_data.items():
                        if hasattr(self, key):
                            setattr(self, key, value)

    def save_config_file(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config_file = self.config_dir / "config.yaml"
        
        config_data = {
            "providers": self.providers,
            "mcp": self.mcp,
            "default_provider": self.default_provider,
            "log_level": self.log_level
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)

    def get_provider_config(self, provider_name: str) -> ProviderConfig:
        provider_data = self.providers.get(provider_name, {})
        
        if provider_name == "openai":
            return OpenAIConfig(**provider_data)
        elif provider_name == "azure_openai":
            return AzureOpenAIConfig(**provider_data)
        elif provider_name == "claude":
            return ClaudeConfig(**provider_data)
        elif provider_name == "ollama":
            return OllamaConfig(**provider_data)
        else:
            return ProviderConfig(**provider_data)

    def get_mcp_config(self) -> MCPConfig:
        return MCPConfig(**self.mcp)