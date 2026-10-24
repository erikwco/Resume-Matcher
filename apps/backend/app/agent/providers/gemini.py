import os
import logging

from google import genai
from typing import Any, Dict
from fastapi.concurrency import run_in_threadpool
from google.genai import types
from google.genai.types import HttpOptions

from ..exceptions import ProviderError
from .base import Provider, EmbeddingProvider

logger = logging.getLogger(__name__)

class GeminiProvider(Provider):
  def __init__(self, api_key : str | None = None,  model: str = "gemini-2.5-flash"):
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
      raise ProviderError("GEMINI_API_KEY is not set")
    self._client = genai.Client(api_key=api_key, http_options=HttpOptions(api_version="v1"))
    self.model = model
    self.instructions = ""

  def _generate_sync(self, prompt: str, options: Dict[str, Any]) -> str:
    try:
      config_params = {}
      if self.instructions:  # Only add system_instruction if not empty
        config_params["system_instruction"] = self.instructions
      config_params.update(options)

      response = self._client.models.generate_content(
        model=self.model,
        contents=prompt,
        config=types.GenerateContentConfig(**config_params)
      )
      return response.text
    except Exception as e:
      logger.error(f"Error generating text with Gemini: {e}")
      raise ProviderError(f"Gemini generation failed: {e}")

  async def __call__(self, prompt: str, **generation_args: Any) -> str:
    """
    Generate text using the Gemini model.
    """
    options = {
      "temperature": generation_args.get("temperature", 0),
      "max_output_tokens": generation_args.get("max_output_tokens", 20000),
      "top_p": generation_args.get("top_p", 0.9),
      "top_k": generation_args.get("top_k", 40),
    }
    return await run_in_threadpool(self._generate_sync, prompt, options)


class GeminiEmbeddingProvider(EmbeddingProvider):
  def __init__(self, api_key: str | None = None, embedding_model: str = "gemini-embedding-001"):
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
      raise ProviderError("GEMINI_API_KEY is not set")
    self._client = genai.Client(api_key=api_key)
    self.embedding_model = embedding_model

  async def embed(self, text: str) -> list[float]:
    """
    Generate embeddings for the given text using the Gemini embedding model.
    """
    try:
      response = self._client.models.embed_content(
        model=self.embedding_model,
        contents=text
      )
      return response.embeddings[0].values
    except Exception as e:
      logger.error(f"Error generating embeddings with Gemini: {e}")
      raise ProviderError(f"Gemini embedding failed: {e}")
