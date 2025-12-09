
from pathlib import Path
from typing import List, Literal

from openai.types.chat import ChatCompletion

from src.design_construct.symbol_reference import ReferenceItem
from src.utils.llms import get_deepseek_client, get_openai_client
from src.utils.run_cmd import CommandExecResult


SYSTEM_PROMPT = Path('./prompts_tools/dependency_resolve_workflow.md').read_text()
USER_INPUT_TEMPLATE = Path('./prompts_tools/dependency_resolve_in.md').read_text()


def _prepare_inputs(
        design_c: str,
        design_h: str,
        gcc_compilation_results: CommandExecResult,
        reference: dict[str, List[ReferenceItem]],
):
    # _COMPILE_RLT_PH = r'{{__COMPILATION_RESULTS__}}'
    _DES_H_PH = r'{{__DESIGN_H__}}'
    _DES_C_PH = r'{{__DESIGN_C__}}'
    _REF_PH = r'{{__REFERENCE_CODE_CONTEXT__}}'

    def _ref_format(ref: ReferenceItem):
        return (
            f"/* {ref.location} */\n"
            + ref.source_snippet.strip()
        )
    
    input_for_each_symbols = list()
    
    for symbol, ref_items in reference.items():
        lns = []
        lns.append(f"{symbol}\n")

        if ref_items:
            lns.append(f"```c\n")
            for ref in ref_items:
                lns.append(_ref_format(ref))
                lns.append("\n")
            lns.append(f"```\n")

        if len(ref_items) == 0:
            lns.append("NOTE: You need to provide a stub implementation based on the design code.\n")
        if len(ref_items) > 1:
            lns.append(
                "NOTE: You need to choose the most appropriate one based on the design code.\n"
            )
        
        input_for_each_symbols.append("".join(lns))

    # if gcc_compilation_results is None:
    #     err = "<First iteration, the dependency is function in reference code>"
    # else:
    #     err = gcc_compilation_results.stderr
    
    input_ = {
        # _COMPILE_RLT_PH: err,
        _DES_H_PH: design_h,
        _DES_C_PH: design_c,
        _REF_PH: "\n".join(input_for_each_symbols),
    }

    system_prompt = USER_INPUT_TEMPLATE
    for ph, ctx in input_.items():
        if ph not in system_prompt:
            raise RuntimeError(f"Cannot find placeholder `{ph}` in system prompt.")
        system_prompt = system_prompt.replace(ph, ctx)

    return system_prompt


def dependency_resolve_deepseek(
        design_c: str,
        design_h: str,
        gcc_compilation_results: CommandExecResult,
        reference: dict[str, List[ReferenceItem]],
        *,
        llm_model: Literal['deepseek-chat', 'deepseek-reasoner'] = 'deepseek-chat',
) -> ChatCompletion:
    input_ = _prepare_inputs(
        design_c, design_h, gcc_compilation_results, reference
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": input_},
    ]
    client = get_deepseek_client()
    return client.chat.completions.create(
        model=llm_model,
        messages=messages,
        temperature=0.1,
    )


def dependency_resolve_gpt5(
        design_c: str,
        design_h: str,
        gcc_compilation_results: CommandExecResult,
        reference: dict[str, List[ReferenceItem]],
        *,
        llm_model: Literal['gpt-5.1-chat-latest'] = 'gpt-5.1-chat-latest',
) -> ChatCompletion:
    kwargs = {
        "instructions": 'You are a professional C language engineer.',
        "model": llm_model,
    }
    input_ = _prepare_inputs(
        design_c, design_h, gcc_compilation_results, reference
    )
    input_ = (
        SYSTEM_PROMPT + "\n\n" + 
        "Below is the user input:\n\n" + input_
    )
    client = get_openai_client()
    return client.responses.create(
        input=input_,
        **kwargs,
    )
