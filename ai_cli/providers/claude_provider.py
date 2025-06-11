from typing import List, Dict, Any, AsyncGenerator
import anthropic
from .base import BaseAIProvider, AIMessage, AIResponse


class ClaudeProvider(BaseAIProvider):
    
    @property
    def provider_name(self) -> str:
        return "claude"

    @property
    def supported_models(self) -> List[str]:
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0"
        ]

    async def initialize(self) -> None:
        api_key = self.config.get("api_key")
        if not api_key:
            raise ValueError("Claude API key is required")
        
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def chat_completion(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AIResponse:
        model = kwargs.get("model", self.config.get("model", "claude-3-sonnet-20240229"))
        max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens", 4000))
        temperature = kwargs.get("temperature", self.config.get("temperature", 0.7))

        system_message = None
        chat_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                chat_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        kwargs_clean = {k: v for k, v in kwargs.items() 
                       if k not in ["model", "max_tokens", "temperature"]}

        response = await self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message,
            messages=chat_messages,
            **kwargs_clean
        )

        return AIResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            },
            metadata={
                "id": response.id,
                "type": response.type,
                "role": response.role,
                "stop_reason": response.stop_reason
            }
        )

    async def stream_completion(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        model = kwargs.get("model", self.config.get("model", "claude-3-sonnet-20240229"))
        max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens", 4000))
        temperature = kwargs.get("temperature", self.config.get("temperature", 0.7))

        system_message = None
        chat_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                chat_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        kwargs_clean = {k: v for k, v in kwargs.items() 
                       if k not in ["model", "max_tokens", "temperature"]}

        async with self._client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message,
            messages=chat_messages,
            **kwargs_clean
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def validate_connection(self) -> bool:
        try:
            test_message = [AIMessage(role="user", content="Hello")]
            await self.chat_completion(test_message, max_tokens=1)
            return True
        except Exception:
            return False