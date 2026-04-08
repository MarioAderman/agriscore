"""Shared LLM clients — singleton factory.

Supports two families:
  - Claude (Anthropic): via Bedrock (IAM auth) or direct API (key-based)
  - OpenAI-compatible: OpenAI, Groq, or any provider with an OpenAI-style API

The Claude client is always available for vision/document tasks, regardless of
which provider the agent loop uses.
"""

import logging

import anthropic
import openai

from app.config import settings

logger = logging.getLogger(__name__)

# Default models per provider
DEFAULT_MODELS: dict[str, str] = {
    "bedrock": "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o",
    "groq": "meta-llama/llama-4-scout-17b-16e-instruct",
}

# Singletons
_claude_client = None
_openai_client = None
_groq_client = None


def active_model() -> str:
    """Return the model ID for the current provider."""
    return settings.llm_model or DEFAULT_MODELS.get(settings.llm_provider, DEFAULT_MODELS["bedrock"])


def get_claude_client() -> anthropic.AsyncAnthropic | anthropic.AsyncAnthropicBedrock:
    """Return a Claude async client. Prefers direct API if key is set, else Bedrock (IAM).

    Used for the agent loop (when provider is anthropic/bedrock) AND for
    vision/document extraction (always, regardless of agent provider).
    """
    global _claude_client
    if _claude_client is not None:
        return _claude_client

    if settings.llm_provider == "bedrock" and not settings.anthropic_api_key:
        _claude_client = anthropic.AsyncAnthropicBedrock(
            aws_region=settings.aws_default_region,
        )
        logger.info("Claude client: Bedrock (%s)", settings.aws_default_region)
    else:
        _claude_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        logger.info("Claude client: direct API")

    return _claude_client


def get_claude_model() -> str:
    """Return the Claude model ID matching the current backend."""
    if settings.llm_model:
        return settings.llm_model
    if settings.llm_provider == "bedrock" and not settings.anthropic_api_key:
        return DEFAULT_MODELS["bedrock"]
    return DEFAULT_MODELS["anthropic"]


def get_openai_client() -> openai.AsyncOpenAI:
    """Return an OpenAI async client."""
    global _openai_client
    if _openai_client is None:
        _openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
    return _openai_client


def get_groq_client() -> openai.AsyncOpenAI:
    """Return a Groq async client (OpenAI-compatible)."""
    global _groq_client
    if _groq_client is None:
        _groq_client = openai.AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )
    return _groq_client
