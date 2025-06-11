from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncGenerator
from pydantic import BaseModel


class AIMessage(BaseModel):
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


class AIResponse(BaseModel):
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseAIProvider(ABC):
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._client = None

    @abstractmethod
    async def initialize(self) -> None:
        pass

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AIResponse:
        pass

    @abstractmethod
    async def stream_completion(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def supported_models(self) -> List[str]:
        pass

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self._client, 'close'):
            await self._client.close()