from typing import Dict, Type
from .base import BaseAIProvider
from .openai_provider import OpenAIProvider
from .claude_provider import ClaudeProvider
from .ollama_provider import OllamaProvider
from .azure_openai_provider import AzureOpenAIProvider


class ProviderFactory:
    _providers: Dict[str, Type[BaseAIProvider]] = {
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
        "ollama": OllamaProvider,
        "azure_openai": AzureOpenAIProvider,
    }

    @classmethod
    def create_provider(
        self, 
        provider_name: str, 
        config: Dict
    ) -> BaseAIProvider:
        if provider_name not in self._providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        provider_class = self._providers[provider_name]
        return provider_class(config)

    @classmethod
    def get_available_providers(cls) -> list[str]:
        return list(cls._providers.keys())

    @classmethod
    def register_provider(
        cls, 
        name: str, 
        provider_class: Type[BaseAIProvider]
    ) -> None:
        cls._providers[name] = provider_class