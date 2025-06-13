from typing import List, Dict, Any, AsyncGenerator, Optional
import openai
from .base import BaseAIProvider, AIMessage, AIResponse, ToolCall


class OpenAIProvider(BaseAIProvider):
    
    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def supported_models(self) -> List[str]:
        return [
            "o3-mini",
            "o3", 
            "o1-mini",
            "o1",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-turbo-preview", 
            "gpt-4o",
            "gpt-4o-mini",
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
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        model = kwargs.get("model", self.config.get("model", "o3-mini"))
        # Try max_completion_tokens first (for o3/o1), fallback to max_tokens
        # Use higher limits for reasoning models
        default_tokens = 16000 if model.startswith(("o3", "o1")) else 4000
        max_tokens = kwargs.get("max_tokens", 
                               self.config.get("max_completion_tokens", 
                                             self.config.get("max_tokens", default_tokens)))
        temperature = kwargs.get("temperature", self.config.get("temperature", 0.7))

        openai_messages = []
        for msg in messages:
            message_dict = {"role": msg.role, "content": msg.content}
            if msg.name:
                message_dict["name"] = msg.name
            openai_messages.append(message_dict)

        # Prepare call parameters
        call_params = {
            "model": model,
            "messages": openai_messages
        }
        
        # o3 and o1 models use max_completion_tokens and don't support temperature
        if model.startswith(("o3", "o1")):
            call_params["max_completion_tokens"] = max_tokens
            # o3/o1 models don't support temperature parameter
        else:
            call_params["max_tokens"] = max_tokens
            call_params["temperature"] = temperature

        # Add tools if provided
        if tools:
            call_params["tools"] = tools
            if tool_choice:
                call_params["tool_choice"] = tool_choice

        response = await self._client.chat.completions.create(**call_params)

        # Handle tool calls
        tool_calls = None
        if response.choices[0].message.tool_calls:
            tool_calls = [
                ToolCall(
                    id=tc.id,
                    function={
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                )
                for tc in response.choices[0].message.tool_calls
            ]

        return AIResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage=response.usage.model_dump() if response.usage else None,
            tool_calls=tool_calls,
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
        model = kwargs.get("model", self.config.get("model", "o3-mini"))
        # Try max_completion_tokens first (for o3/o1), fallback to max_tokens
        # Use higher limits for reasoning models
        default_tokens = 16000 if model.startswith(("o3", "o1")) else 4000
        max_tokens = kwargs.get("max_tokens", 
                               self.config.get("max_completion_tokens", 
                                             self.config.get("max_tokens", default_tokens)))
        temperature = kwargs.get("temperature", self.config.get("temperature", 0.7))

        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Prepare stream parameters
        stream_params = {
            "model": model,
            "messages": openai_messages,
            "stream": True
        }
        
        # o3 and o1 models use max_completion_tokens and don't support temperature
        if model.startswith(("o3", "o1")):
            stream_params["max_completion_tokens"] = max_tokens
            # o3/o1 models don't support temperature parameter
        else:
            stream_params["max_tokens"] = max_tokens
            stream_params["temperature"] = temperature

        stream = await self._client.chat.completions.create(**stream_params)

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def validate_connection(self) -> bool:
        try:
            await self._client.models.list()
            return True
        except Exception:
            return False