from typing import List, Dict, Any, AsyncGenerator
import httpx
import json
from .base import BaseAIProvider, AIMessage, AIResponse


class OllamaProvider(BaseAIProvider):
    
    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def supported_models(self) -> List[str]:
        return [
            "llama2",
            "llama2:13b",
            "llama2:70b",
            "codellama",
            "codellama:13b",
            "mistral",
            "mixtral",
            "neural-chat",
            "starling-lm"
        ]

    async def initialize(self) -> None:
        base_url = self.config.get("base_url", "http://localhost:11434")
        self._client = httpx.AsyncClient(base_url=base_url)

    async def chat_completion(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AIResponse:
        model = kwargs.get("model", self.config.get("model", "llama2"))
        
        ollama_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        payload = {
            "model": model,
            "messages": ollama_messages,
            "stream": False,
            "options": {}
        }

        if "temperature" in kwargs or "temperature" in self.config:
            payload["options"]["temperature"] = kwargs.get(
                "temperature", 
                self.config.get("temperature", 0.7)
            )

        if "max_tokens" in kwargs or "max_tokens" in self.config:
            payload["options"]["num_predict"] = kwargs.get(
                "max_tokens", 
                self.config.get("max_tokens", 4000)
            )

        response = await self._client.post("/api/chat", json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        return AIResponse(
            content=data["message"]["content"],
            model=data["model"],
            usage={
                "prompt_eval_count": data.get("prompt_eval_count", 0),
                "eval_count": data.get("eval_count", 0),
                "total_duration": data.get("total_duration", 0)
            },
            metadata={
                "created_at": data.get("created_at"),
                "done": data.get("done", True)
            }
        )

    async def stream_completion(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        model = kwargs.get("model", self.config.get("model", "llama2"))
        
        ollama_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        payload = {
            "model": model,
            "messages": ollama_messages,
            "stream": True,
            "options": {}
        }

        if "temperature" in kwargs or "temperature" in self.config:
            payload["options"]["temperature"] = kwargs.get(
                "temperature", 
                self.config.get("temperature", 0.7)
            )

        if "max_tokens" in kwargs or "max_tokens" in self.config:
            payload["options"]["num_predict"] = kwargs.get(
                "max_tokens", 
                self.config.get("max_tokens", 4000)
            )

        async with self._client.stream("POST", "/api/chat", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            content = data["message"]["content"]
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue

    async def validate_connection(self) -> bool:
        try:
            response = await self._client.get("/api/tags")
            return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        try:
            response = await self._client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception:
            return self.supported_models