
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List

from openai.types.chat import ChatCompletion

from ..symbol_reference import ReferenceItem
from ...csource.csource import CSource
from ...utils.llms import (
    GPT5_TEXT_VERBOSITY_SELS, GPT5_MODEL_SELS, GPT5_REASONING_EFFORT_SELS, 
    OPENAI_MODEL_SELS, get_deepseek_client,
    get_openai_client, get_poe_client
)



@lru_cache(maxsize=1)
def _get_system_prompt(
    enable_placeholder: bool = True,
) -> str:
    # TODO: Currently always enables placeholder prompt.
    if enable_placeholder:
        return Path('prompts_tools/design_merge_v2.md').read_text()
    else:
        return Path('prompts_tools/design_merge.md').read_text()


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


_SYM_TO_IMPL_PH = r'{{__SYMBOLS_TO_IMPLEMENT__}}'
_DES_H_PH = r'{{__DESIGN_H__}}'
_DES_C_PH = r'{{__DESIGN_C__}}'
_REF_PH = r'{{__REFERENCE_CODE_CONTEXT__}}'

def _ref_format(ref: ReferenceItem):
    return (
        f"/* {ref.location} */\n"
        + ref.source_snippet.strip()
    )

def _prepare_inputs(
        design_c: str | CSource,
        design_h: str | CSource,
        symbol_to_implement: str | Iterable[str],
        reference: List[ReferenceItem],
):
    if isinstance(symbol_to_implement, str):
        symbol_to_implement = [symbol_to_implement]
    symbol_str = "\n".join(symbol_to_implement)

    design_c = design_c.as_str if isinstance(design_c, CSource) else design_c
    design_h = design_h.as_str if isinstance(design_h, CSource) else design_h

    ref_code = "\n\n".join(_ref_format(r) for r in reference)

    input_ = {
        _SYM_TO_IMPL_PH: symbol_str,
        _DES_H_PH: design_h,
        _DES_C_PH: design_c,
        _REF_PH: ref_code,
    }

    system_prompt = _get_system_prompt()
    for ph, ctx in input_.items():
        if ph not in system_prompt:
            raise RuntimeError(f"Cannot find placeholder `{ph}` in system prompt.")
        system_prompt = system_prompt.replace(ph, ctx)

    return system_prompt


def design_merge_gpt5(
        design_c: str | CSource,
        design_h: str | CSource,
        symbol_to_implement: str | Iterable[str],
        reference: List[ReferenceItem],
        *,
        model: GPT5_MODEL_SELS = 'gpt-5-codex',
        reasoning_effort: GPT5_REASONING_EFFORT_SELS = 'medium',
        text_verbosity: GPT5_TEXT_VERBOSITY_SELS = 'medium',
):
    args_ = _prepare_gpt5_args(
        model, reasoning_effort, text_verbosity
    )
    input_ = _prepare_inputs(
        design_c, design_h, symbol_to_implement, reference
    )

    client = get_openai_client()
    return client.responses.create(input=input_, **args_)


def design_merge_poe_claude_sonnet_4_5(
        design_c: str | CSource,
        design_h: str | CSource,
        symbol_to_implement: str | Iterable[str],
        reference: List[ReferenceItem]
) -> ChatCompletion:
    input_ = _prepare_inputs(
        design_c, design_h, symbol_to_implement, reference
    )
    messages = [
        {"role": "system", "content": "You are a professional C language engineer."},
        {"role": "user", "content": input_},
    ]
    client = get_poe_client()
    return client.chat.completions.create(
        model="Claude-Sonnet-4.5",
        messages=messages,
        temperature=0.2,
        extra_body={"thinking_budget": 8192}
    )


def design_merge_deepseek(
        design_c: str | CSource,
        design_h: str | CSource,
        symbol_to_implement: str | Iterable[str],
        reference: List[ReferenceItem]
) -> ChatCompletion:
    input_ = _prepare_inputs(
        design_c, design_h, symbol_to_implement, reference
    )
    messages = [
        {"role": "system", "content": "You are a professional C language engineer."},
        {"role": "user", "content": input_},
    ]
    client = get_deepseek_client()
    return client.chat.completions.create(
        model="deepseek-reasoner",
        messages=messages,
        temperature=0.1,
    )


def design_merge_openai(
        design_c: str | CSource,
        design_h: str | CSource,
        symbol_to_implement: str | Iterable[str],
        reference: List[ReferenceItem],
        *,
        model: OPENAI_MODEL_SELS = 'gpt-4.1',
):
    args_ = _prepare_openai_args(model)
    input_ = _prepare_inputs(
        design_c, design_h, symbol_to_implement, reference
    )
    client = get_openai_client()
    return client.responses.create(input=input_, **args_)
