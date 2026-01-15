"""
Ollama client for LLM integration.
"""
import json
from typing import Any, AsyncGenerator, List, Optional

import httpx
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OllamaClient:
    """Client for interacting with Ollama LLM server."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        """
        Initialize Ollama client.

        Args:
            base_url: Base URL for Ollama server
            model: Default model to use
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.timeout = timeout or settings.ollama_timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None] | str:
        """
        Generate completion from Ollama.

        Args:
            prompt: User prompt
            model: Model to use (defaults to instance model)
            system: System prompt
            temperature: Sampling temperature
            stream: Whether to stream the response
            **kwargs: Additional generation parameters

        Returns:
            Generated text or async generator for streaming
        """
        model = model or self.model
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": settings.ollama_num_predict,
                **kwargs,
            },
        }

        if system:
            payload["system"] = system

        logger.info("Generating completion", model=model, stream=stream)

        if stream:
            return self._stream_generate(url, payload)
        else:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")

    async def _stream_generate(
        self, url: str, payload: dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """
        Stream generate completion.

        Args:
            url: API endpoint URL
            payload: Request payload

        Yields:
            Chunks of generated text
        """
        async with self.client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]

    async def chat(
        self,
        messages: List[dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None] | dict[str, Any]:
        """
        Chat completion using Ollama.

        Args:
            messages: List of messages with 'role' and 'content'
            model: Model to use
            temperature: Sampling temperature
            stream: Whether to stream the response
            **kwargs: Additional parameters

        Returns:
            Response dict or async generator for streaming
        """
        model = model or self.model
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": settings.ollama_num_predict,
                "top_k": 20,  # Limit sampling to top 20 tokens for speed
                "top_p": 0.9,  # Nucleus sampling for faster generation
                "repeat_penalty": 1.1,  # Prevent repetition
                **kwargs,
            },
        }

        logger.info("Chat completion", model=model, num_messages=len(messages))

        if stream:
            # Return the async generator directly (no await needed)
            return self._stream_chat(url, payload)
        else:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

    def _stream_chat(
        self, url: str, payload: dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion.

        Args:
            url: API endpoint URL
            payload: Request payload

        Yields:
            Chunks of generated text
        """
        # This is a synchronous function that returns an async generator
        async def _generate():
            async with self.client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
        
        return _generate()

    async def list_models(self) -> List[dict[str, Any]]:
        """
        List available models.

        Returns:
            List of model information dicts
        """
        url = f"{self.base_url}/api/tags"
        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        return result.get("models", [])

    async def check_health(self) -> bool:
        """
        Check if Ollama server is healthy.

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = await self.client.get(url)
            return response.status_code == 200
        except Exception as e:
            logger.error("Ollama health check failed", error=str(e))
            return False

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()


# Global Ollama client instance
ollama_client = OllamaClient()
