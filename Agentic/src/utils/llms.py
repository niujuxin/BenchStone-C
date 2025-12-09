
from typing import Literal
import os
from functools import lru_cache
from dataclasses import dataclass

from openai import AsyncOpenAI, OpenAI


@dataclass
class OpenAITokenUsage:
    input_tokens: int
    output_tokens: int
    total_tokens: int
    
    @classmethod
    def from_json(cls, data: dict) -> 'OpenAITokenUsage':
        return cls(
            input_tokens=data.get('input_tokens', data.get('prompt_tokens', 0)),
            output_tokens=data.get('output_tokens', data.get('completion_tokens', 0)),
            total_tokens=data.get('total_tokens')
        )


@lru_cache(maxsize=1)
def get_openai_client(use_async: bool = False) -> OpenAI:

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    if use_async:
        return AsyncOpenAI(api_key=api_key)
    else:
        return OpenAI(api_key=api_key)


@lru_cache(maxsize=1)
def get_poe_client(use_async: bool = False):
    api_key = os.getenv("POE_API_KEY")
    if not api_key:
        raise ValueError("POE_API_KEY environment variable not set")
    
    client = OpenAI(
        api_key = api_key,
        base_url = "https://api.poe.com/v1",
    )
    return client


@lru_cache(maxsize=1)
def get_deepseek_client(use_async: bool = False):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable not set")
    
    client = OpenAI(
        api_key = api_key,
        base_url = "https://api.deepseek.com",
    )
    return client


OPENAI_MODEL_SELS = Literal['gpt-4.1', 'gpt-4.1-mini']
GPT5_MODEL_SELS = Literal['gpt-5', 'gpt-5-mini', 'gpt-5-nano', 'gpt-5-codex']
DEEPSEEK_MODEL_SELS = Literal['deepseek-chat', 'deepseek-reasoner']

GPT5_REASONING_EFFORT_SELS = Literal['minimal', 'low', 'medium', 'high']
GPT5_TEXT_VERBOSITY_SELS = Literal['low', 'medium', 'high']
