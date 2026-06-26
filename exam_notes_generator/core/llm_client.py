from __future__ import annotations

from openai import OpenAI
import os
import random

from .config import config
from .logger import get_logger


logger = get_logger(__name__)


def _get_client() -> OpenAI:
    """Priority: Bedrock > Groq > Ollama."""
    bedrock_keys = os.getenv("BEDROCK_API_KEY", "")
    if bedrock_keys:
        import httpx
        keys = bedrock_keys.split(",")
        key = random.choice(keys).strip()
        region = os.getenv("BEDROCK_REGION", "us-east-1")
        base_url = f"https://bedrock-mantle.{region}.api.aws/v1"
        http_client = httpx.Client(headers={"Host": "bedrock.amazonaws.com"})
        return OpenAI(base_url=base_url, api_key=key, http_client=http_client)

    groq_keys = os.getenv("GROQ_API_KEY", "")
    if groq_keys:
        keys = groq_keys.split(",")
        key = random.choice(keys).strip()
        return OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)

    return OpenAI(base_url=config.ollama_base_url, api_key="ollama")


def _get_provider() -> str:
    """Identify which provider is active."""
    if os.getenv("BEDROCK_API_KEY", ""):
        return "bedrock"
    if os.getenv("GROQ_API_KEY", ""):
        return "groq"
    return "ollama"


def check_llm() -> tuple[bool, str]:
    provider = _get_provider()
    try:
        if provider == "bedrock":
            return True, f"Amazon Bedrock ready: {os.getenv('BEDROCK_MODEL', 'deepseek.v3.2')}"
        elif provider == "groq":
            return True, f"Groq API ready: llama-3.3-70b-versatile"
        else:
            client = _get_client()
            models = client.models.list()
            names = [model.id for model in models.data]
            if config.ollama_model not in names:
                return False, f"Ollama is running, but {config.ollama_model} is not installed."
            return True, f"Local Ollama ready: {config.ollama_model}"
    except Exception as exc:
        logger.warning("LLM check failed: %s", exc)
        return False, f"LLM is not reachable: {exc}"


def generate_with_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    context_length: int,
) -> str:
    """Generate with Bedrock, Groq, or local Ollama model."""

    client = _get_client()
    provider = _get_provider()

    if provider == "bedrock":
        model = os.getenv("BEDROCK_MODEL", "deepseek.v3.2")
        extra_body = {}
    elif provider == "groq":
        model = "llama-3.3-70b-versatile"
        extra_body = {}
    else:
        model = config.ollama_model
        extra_body = {
            "options": {
                "num_ctx": context_length,
                "num_gpu": -1,
                "flash_attn": True,
            }
        }

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        extra_body=extra_body if extra_body else None,
    )
    return response.choices[0].message.content or ""
