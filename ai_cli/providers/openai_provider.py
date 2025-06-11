from typing import List, Dict, Any, AsyncGenerator
import openai
from .base import BaseAIProvider, AIMessage, AIResponse


class OpenAIProvider(BaseAIProvider):
    
    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def supported_models(self) -> List[str]:
        return [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]

    async def initialize(self) -> None:
        api_key = self.config.get("api_key")
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self._client = openai.AsyncOpenAI(api_key=api_key)

    async def chat_completion(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AIResponse:
        model = kwargs.get("model", self.config.get("model", "gpt-4"))
        max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens", 4000))
        temperature = kwargs.get("temperature", self.config.get("temperature", 0.7))

        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = await self._client.chat.completions.create(
            model=model,
            messages=openai_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

        return AIResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage=response.usage.dict() if response.usage else None,
            metadata={
                "finish_reason": response.choices[0].finish_reason,
                "created": response.created,
                "id": response.id
            }
        )

    async def stream_completion(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        model = kwargs.get("model", self.config.get("model", "gpt-4"))
        max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens", 4000))
        temperature = kwargs.get("temperature", self.config.get("temperature", 0.7))

        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        stream = await self._client.chat.completions.create(
            model=model,
            messages=openai_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
            **kwargs
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def validate_connection(self) -> bool:
        try:
            await self._client.models.list()
            return True
        except Exception:
            return False