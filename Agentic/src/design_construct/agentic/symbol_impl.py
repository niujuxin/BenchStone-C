
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

from openai.types.responses import Response

from ...utils.llms import (
    GPT5_TEXT_VERBOSITY_SELS, GPT5_MODEL_SELS, GPT5_REASONING_EFFORT_SELS, 
    OPENAI_MODEL_SELS,
    get_openai_client
)


@lru_cache(maxsize=1)
def _get_system_prompt() -> str:
    return Path('prompts_tools/symbol_impl.md').read_text()


def _prepare_input(
        symbol_context: Dict[str, str | List[str]],
) -> str:

    blocks = list()

    for symbol, context in symbol_context.items():
        ctx = ''.join(context) if isinstance(context, list) else context
        blocks.append(
            f"### {symbol}\n\n"
            f"```c\n"
            f"{ctx}\n"
            f"```\n"
        )

    input_ = (
        _get_system_prompt() +
        f"\n\nYou have {len(symbol_context)} symbols to implement:\n\n" +
        '\n\n'.join(blocks)
    )

    return input_


def _prepare_gpt5_args(
        model: GPT5_MODEL_SELS,
        reasoning_effort: GPT5_REASONING_EFFORT_SELS,
        text_verbosity: GPT5_TEXT_VERBOSITY_SELS,
) -> Dict:
    return {
        "instructions": 'You are a professional C language engineer.',
        "model": model,
        "reasoning": { "effort": reasoning_effort },
        "text": { "verbosity": text_verbosity },
    }

def _prepare_openai_args(
        model: OPENAI_MODEL_SELS,
) -> Dict:
    return {
        "instructions": 'You are a professional C language engineer.',
        "model": model,
    }


def symbol_impl_gpt5(
        symbol_context: Dict[str, str | List[str]],
        *,
        model: GPT5_MODEL_SELS = 'gpt-5-mini',
        reasoning_effort: GPT5_REASONING_EFFORT_SELS = 'low',
        text_verbosity: GPT5_TEXT_VERBOSITY_SELS = 'low',
) -> Response:
    input_ = _prepare_input(symbol_context)
    args = _prepare_gpt5_args(
        model, reasoning_effort, text_verbosity,
    )
    return get_openai_client().responses.create(input=input_, **args)


async def symbol_impl_gpt5_async(
        symbol_context: Dict[str, str | List[str]],
        *,
        model: GPT5_MODEL_SELS = 'gpt-5-mini',
        reasoning_effort: GPT5_REASONING_EFFORT_SELS = 'low',
        text_verbosity: GPT5_TEXT_VERBOSITY_SELS = 'low',
) -> Response:
    input_ = _prepare_input(symbol_context)
    args = _prepare_gpt5_args(
        model, reasoning_effort, text_verbosity,
    )
    return await get_openai_client(
        use_async=True).responses.create(input=input_, **args)


def symbol_impl_openai(
        symbol_context: Dict[str, str | List[str]],
        *,
        model: OPENAI_MODEL_SELS = 'gpt-4.1',
) -> Response:
    input_ = _prepare_input(symbol_context)
    args = _prepare_openai_args(model,)
    return get_openai_client().responses.create(input=input_, **args)


async def symbol_impl_openai_async(
        symbol_context: Dict[str, str | List[str]],
        *,
        model: OPENAI_MODEL_SELS = 'gpt-4.1',
) -> Response:
    input_ = _prepare_input(symbol_context)
    args = _prepare_openai_args(model,)
    return await get_openai_client(
        use_async=True).responses.create(input=input_, **args)
