
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

from ...csource.csource import CSource
from ...utils.llms import (
    GPT5_TEXT_VERBOSITY_SELS, GPT5_MODEL_SELS, GPT5_REASONING_EFFORT_SELS, 
    get_openai_client
)


@lru_cache(maxsize=1)
def _get_system_prompt() -> str:
    return Path('prompts_tools/h_design_top_func_extract.md').read_text()


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


_DES_NAME_PH = r'{{__DESIGN_NAME__}}'
_REPO_NAME_PH = r'{{__REPO_NAME__}}'
_ALL_CODES_PH = r'{{__ALL_CODES__}}'


def _prepare_inputs(
        design_name: str,
        repo_name: str,
        all_codes: Dict[Path | str, str | CSource],
):
    
    code_blocks: List[str] = []
    for fp, code in all_codes.items():
        code_blocks.append(
            f"**{fp.as_posix() if isinstance(fp, Path) else fp}**:\n"
            f"```c\n" + 
            (code.as_str if isinstance(code, CSource) else code) +
            f"```\n"
        )

    input_ = {
        _DES_NAME_PH: design_name,
        _REPO_NAME_PH: repo_name,
        _ALL_CODES_PH: '\n'.join(code_blocks),
    }

    system_prompt = _get_system_prompt()
    for ph, ctx in input_.items():
        if ph not in system_prompt:
            raise RuntimeError(f"Cannot find placeholder `{ph}` in system prompt.")
        system_prompt = system_prompt.replace(ph, ctx)

    return system_prompt


def h_design_top_func_extract_gpt5(
        design_name: str,
        repo_name: str,
        all_codes: Dict[Path | str, str | CSource],
        *,
        model: GPT5_MODEL_SELS = 'gpt-5-codex',
        reasoning_effort: GPT5_REASONING_EFFORT_SELS = 'low',
        text_verbosity: GPT5_TEXT_VERBOSITY_SELS = 'medium',
) -> str:
    
    input_ = _prepare_inputs(
        design_name=design_name,
        repo_name=repo_name,
        all_codes=all_codes,
    )

    gpt5_args = _prepare_gpt5_args(
        model=model,
        reasoning_effort=reasoning_effort,
        text_verbosity=text_verbosity,
    )

    client = get_openai_client()
    return client.responses.create(input=input_, **gpt5_args)
