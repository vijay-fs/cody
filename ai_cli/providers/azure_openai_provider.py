from typing import List, Dict, Any, AsyncGenerator
try:
    from openai import AsyncAzureOpenAI
except ImportError:
    AsyncAzureOpenAI = None
from .base import BaseAIProvider, AIMessage, AIResponse


class AzureOpenAIProvider(BaseAIProvider):
    
    @property
    def provider_name(self) -> str:
        return "azure_openai"

    @property
    def supported_models(self) -> List[str]:
        return [
            "gpt-4",
            "gpt-4-32k",
            "gpt-4-turbo",
            "gpt-35-turbo",
            "gpt-35-turbo-16k"
        ]

    async def initialize(self) -> None:
        if AsyncAzureOpenAI is None:
            raise ImportError("Azure OpenAI is not available. Install with: pip install openai")
            
        api_key = self.config.get("api_key")
        endpoint = self.config.get("endpoint")
        api_version = self.config.get("api_version", "2024-02-01")
        
        if not api_key:
            raise ValueError("Azure OpenAI API key is required")
        if not endpoint:
            raise ValueError("Azure OpenAI endpoint is required")
        
        self._client = AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version
        )

    async def chat_completion(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AIResponse:
        deployment_name = kwargs.get("model", self.config.get("deployment_name"))
        if not deployment_name:
            raise ValueError("Azure OpenAI deployment name is required")
            
        max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens", 4000))
        temperature = kwargs.get("temperature", self.config.get("temperature", 0.7))

        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Remove Azure-specific params from kwargs before passing to API
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ["model", "max_tokens", "temperature"]}

        response = await self._client.chat.completions.create(
            model=deployment_name,
            messages=openai_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **clean_kwargs
        )

        return AIResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage=response.usage.model_dump() if response.usage else None,
            metadata={
                "finish_reason": response.choices[0].finish_reason,
                "created": response.created,
                "id": response.id,
                "deployment": deployment_name
            }
        )

    async def stream_completion(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        deployment_name = kwargs.get("model", self.config.get("deployment_name"))
        if not deployment_name:
            raise ValueError("Azure OpenAI deployment name is required")
            
        max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens", 4000))
        temperature = kwargs.get("temperature", self.config.get("temperature", 0.7))

        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Remove Azure-specific params from kwargs before passing to API
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ["model", "max_tokens", "temperature"]}

        stream = await self._client.chat.completions.create(
            model=deployment_name,
            messages=openai_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
            **clean_kwargs
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def validate_connection(self) -> bool:
        try:
            # Try to list deployments to validate connection
            response = await self._client.models.list()
            return True
        except Exception:
            return False

    async def list_deployments(self) -> List[str]:
        try:
            response = await self._client.models.list()
            return [model.id for model in response.data]
        except Exception:
            return []