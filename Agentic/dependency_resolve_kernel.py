from __future__ import annotations

from pathlib import Path
import time
from typing import List, Tuple
from uuid import uuid4
import logging

from openai.types.responses import Response
from openai.types.chat import ChatCompletion

from src.csource import CSource
from src.design_construct.code_editor import span_replace_many
from src.design_construct.code_placeholder import (
    CodePlaceholder, ReplRange, Token, 
    placeholder_composition_type, 
    placeholder_global_variable, replace_back_placeholder
)
from src.design_construct.extract_gcc_incomplete_types import extract_incomplete_types
from src.design_construct.schema_config import DesignMetaV2
from src.design_construct.forward_decl_remove import remove_forward_decls
from src.design_construct.schema_trace import (
    Diagnostics, IncrementalConstructAttemptV2, SourceBundle, TraceStep,
)
from src.utils.code_extract import extract_fenced_code_blocks
from src.design_construct.symbol_reference import (
    SymbolImplReference, prepare_symbol_reference, ReferenceItem
)
from src.design_construct.extract_unresolved import (
    parse_gcc_unresolved_symbol, gcc_compile,
)

from dependency_resolve_agentic import (
    dependency_resolve_deepseek,
    dependency_resolve_gpt5
)


# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DESIGN_C_FNAME = 'design.c'
DESIGN_H_FNAME = 'design.h'


def diagnose(
        src: SourceBundle,
        *,
        design_c_fn: str = DESIGN_C_FNAME,
        design_h_fn: str = DESIGN_H_FNAME,
) -> Diagnostics:
    csrc_c = CSource(src.c)
    csrc_h = CSource(src.header)
    removed_symbols, new_designs = remove_forward_decls(
        [csrc_c, csrc_h]
    )
    # design_c, design_h = new_designs

    # Detect if `<math.h>` is needed
    use_math_h = False
    for inc in (csrc_c.includes + csrc_h.includes):
        target = inc.include_target.strip()
        if target in ('math.h', '<math.h>', '"math.h"'):
            use_math_h = True

    compile_rlt = gcc_compile(
        design_c_fn, csrc_c.as_str, 
        design_h_fn, csrc_h.as_str,
        use_math_h=use_math_h,
    )
    
    gcc_unresolved_symbols = [
        sym.symbol
        for sym in parse_gcc_unresolved_symbol(compile_rlt.stderr)
    ]

    gcc_lns = [line for line in compile_rlt.stderr.splitlines() if line.strip()]
    gcc_imcomplete_types = extract_incomplete_types(gcc_lns)

    return Diagnostics(
        gcc_result=compile_rlt,
        removed_forward_symbols=tuple(removed_symbols),
        unresolved_symbols=tuple(gcc_unresolved_symbols),
        gcc_extra_incomplete_types=tuple(gcc_imcomplete_types),
    )


def design_compress(
        csource: CSource
) -> Tuple[CSource, List[CodePlaceholder]]:
    
    replacements: List[Tuple[ReplRange, Token]] = []
    placeholders: List[CodePlaceholder] = []

    def _str_of(src: bytes, repl_range: ReplRange) -> str:
        return src[repl_range[0]:repl_range[1]].decode(
            'utf-8', errors='ignore')

    def _add_ph(ph: Tuple[ReplRange, Token]) -> None:
        if ph is None:
            return
        repl_range, token = ph
        replacements.append((repl_range, token))
        placeholders.append(
            CodePlaceholder(
                token=token,
                original_code=_str_of(csource.as_bytes, repl_range)
            )
        )

    if False:
        for comp_type in csource.composite_types:
            ph = placeholder_composition_type(comp_type)
            _add_ph(ph)
    
    if True:
        for glob_var in csource.global_variables:
            ph = placeholder_global_variable(glob_var)
            _add_ph(ph)
    
    replaced_bytes = span_replace_many(
        csource.as_bytes,
        replacements
    )
    compressed_csource = CSource(replaced_bytes)
    return compressed_csource, placeholders

def search(
        design_meta: DesignMetaV2,
        all_steps: List[TraceStep],
        *,
        csource_dict: dict[Path, CSource],
        max_iter: int = 10,
        immed_dump_c_to: Path | None = None,
        immed_dump_h_to: Path | None = None,
        #
        max_trace_steps: int = 35,
        enable_placeholder: bool = False,
        llm_version = 'deepseek-chat',
        verbose: bool = False,
):
    if immed_dump_c_to:
        immed_dump_c_to = Path(immed_dump_c_to)
        immed_dump_c_to.parent.mkdir(parents=True, exist_ok=True)   
    if immed_dump_h_to:
        immed_dump_h_to = Path(immed_dump_h_to)
        immed_dump_h_to.parent.mkdir(parents=True, exist_ok=True)

    iteration = 0
    while True:
        if iteration >= max_iter:
            break
        iteration += 1
        verbose and logger.info(f"=== Iteration {iteration} ===")

        if all_steps:
            if len(all_steps) >= max_trace_steps:
                verbose and logger.info(
                    f" Reached max trace steps {max_trace_steps}, stopping."
                )
                break
            parent_step = all_steps[-1]
            curr_design = parent_step.attempt.extracted_design
            llm_reported_missing_symbols = parent_step.attempt.llm_reported_missing_symbols
            curr_diagnostic = diagnose(curr_design)
        else:
            # If no valid step exists, start from an empty design
            verbose and logger.info(" Starting from an empty design.")
            parent_step = None
            curr_design = SourceBundle.initial_empty(
                header_file_name=DESIGN_H_FNAME,
            )
            llm_reported_missing_symbols = tuple()
            curr_diagnostic = Diagnostics(
                gcc_result=None,
                removed_forward_symbols=(),
                unresolved_symbols=tuple([design_meta.function_name, ])
            )
        
        assert isinstance(curr_design, SourceBundle)
        assert isinstance(curr_diagnostic, Diagnostics)

        # Add LLM resolved symbols from last iteration
        curr_diagnostic.llm_indicated_missing_symbols = llm_reported_missing_symbols

        syms = curr_diagnostic.all_unresolved_symbols
        if not syms:
            verbose and logger.info(" All symbols have been resolved.")
            return

        if len(syms) > 5:
            keep_for_next_syms = syms[5:]
            syms = syms[:5]
        else:
            keep_for_next_syms = []

        sym_ref_map: dict[str, SymbolImplReference] = {}
        for sym in syms: # Always get all symbols afresh
            sel_csrc_dict = csource_dict
            if parent_step is None:
                # For the first iteration, only use entry files
                # to avoid picking up irrelevant functions
                sel_csrc_dict = {
                    design_meta.function_location: 
                    csource_dict[design_meta.function_location] 
                }
                
            sym_ref = prepare_symbol_reference(
                sym,  
                sel_csrc_dict,
                use_code_placeholder=enable_placeholder,
            )
            sym_ref_map[sym] = sym_ref
        
        symbols_this_iter: List[str] = list(sym_ref_map.keys())

        reference: dict[str, List[ReferenceItem]] = {}
        for sym, ref_items in sym_ref_map.items():
            deterministed_resolved = ref_items.deterministic_resolve()
            if deterministed_resolved is not None:
                reference[sym] = [deterministed_resolved[1], ]
            else:
                reference[sym] = ref_items.to_flattened_list()

        verbose and logger.info(f" Targeting:")
        if verbose:
            for sym, ref_items in reference.items():
                logger.info(f"  Symbol: {sym}, {len(ref_items)} reference items.")

        ref_placeholders = []
        if enable_placeholder:
            for ref_items in reference.values():
                for ref_item in ref_items:
                    if ref_item.placeholder is not None:
                        ref_placeholders.append(ref_item.placeholder)

        cmp_design_c = CSource(curr_design.c)
        cmp_design_h = CSource(curr_design.header)
        des_placeholder = []

        if enable_placeholder:
            des_placeholder: List[CodePlaceholder] = []
            cmp_design_c, c_phs = design_compress(cmp_design_c)
            cmp_design_h, h_phs = design_compress(cmp_design_h)
            des_placeholder.extend(c_phs)
            des_placeholder.extend(h_phs)
        
        retry_count = 0
        try:
            stime = time.time()
            if llm_version.startswith('gpt'):
                response = dependency_resolve_gpt5(
                    design_c=cmp_design_c.as_str,
                    design_h=cmp_design_h.as_str,
                    gcc_compilation_results=curr_diagnostic.gcc_result,
                    reference=reference,
                    llm_model=llm_version,
                )
                output_text = response.output_text
            elif llm_version.startswith('claude'):
                raise NotImplementedError("Claude integration is not implemented.")
            elif llm_version.startswith('deepseek'):
                response = dependency_resolve_deepseek(
                    design_c=cmp_design_c.as_str,
                    design_h=cmp_design_h.as_str,
                    gcc_compilation_results=curr_diagnostic.gcc_result,
                    reference=reference,
                    llm_model=llm_version,
                )
                output_text = response.choices[0].message.content
            else:
                raise ValueError(f"Unsupported llm_version: {llm_version}")
            etime = time.time()
            llm_response_time_elapsed = etime - stime
            verbose and logger.info(f" LLM response in {llm_response_time_elapsed:.1f}s.")
        except Exception as e:
            # Skip this iteration on any error
            # The trace remains unchanged and 
            # the next iteration will retry from the same state
            verbose and logger.error(" LLM call failed.")
            verbose and logger.error(f"  Error: {e}")
            retry_count += 1
            if retry_count >= 3:
                raise e
            # Sleep for a while before retrying
            time.sleep(5 ** retry_count)
            continue

        code_blocks = extract_fenced_code_blocks(output_text)
        if not (2 <= len(code_blocks) <= 3):
            # Skip this iteration if code blocks are not found correctly
            # The trace remains unchanged and 
            # the next iteration will retry from the same state
            verbose and logger.error(" Failed to extract code blocks.")
            continue

        new_h = CSource(code_blocks[0]['code'])
        new_c = CSource(code_blocks[1]['code'])
        
        if len(code_blocks) == 3:
            _llm_syms = code_blocks[2]['code'].splitlines()
            _llm_syms = [ln.strip() for ln in _llm_syms if ln.strip()]

            # For each symbols, it should only contain
            # the symbol name without extra info
            accepted_chars = set(
                "abcdefghijklmnopqrstuvwxyz"
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                "0123456789_"
            )
            def _is_valid_sym(s: str) -> bool:
                return all((ch in accepted_chars) for ch in s)
            _llm_syms = [s for s in _llm_syms if _is_valid_sym(s)]

        else:
            _llm_syms = []

        # Restore placeholders in reference
        if enable_placeholder:
            phs = ref_placeholders + des_placeholder
            new_h_bytes = replace_back_placeholder(new_h.as_bytes, phs)
            new_c_bytes = replace_back_placeholder(new_c.as_bytes, phs)
            new_h = CSource(new_h_bytes)
            new_c = CSource(new_c_bytes)

        # NOTE: For this search() function, only valid steps are appended
        # to the trace. Invalid steps are simply skipped.
        attempt = IncrementalConstructAttemptV2(
            references=reference,
            llm_response_dumps=response.model_dump_json(),
            extracted_design=SourceBundle(
                c=new_c.as_str, header=new_h.as_str
            ),
            llm_response_time_elapsed=llm_response_time_elapsed,
            llm_reported_missing_symbols=tuple(list(_llm_syms) + list(keep_for_next_syms))
        )

        trace_step = TraceStep(
            uid=uuid4().hex,
            initial_design=curr_design,
            diagnostic=curr_diagnostic,
            target_symbols=tuple(symbols_this_iter),    
            attempt=attempt,
            #
            # ref_placeholders are saved by the reference items,
            # while des_placeholder are saved by the design itself.
            placeholders=(None if not enable_placeholder 
                          else tuple(des_placeholder))
        )

        if immed_dump_c_to:
            immed_dump_c_to.write_bytes(new_c.as_bytes)
        if immed_dump_h_to:
            immed_dump_h_to.write_bytes(new_h.as_bytes)

        all_steps.append(trace_step)

        # NOTE: `all_steps` is separate from `trace.steps`.
        # `all_steps` exists only within search() 
        # to log validated steps and never mutates `trace.steps`.
        yield (
            # Used for linking in the trace
            parent_step.uid if parent_step else None,
            # Every validated step is yielded 
            # so callers can process them externally.
            trace_step
        )
