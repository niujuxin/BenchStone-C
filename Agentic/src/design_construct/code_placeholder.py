import secrets
from dataclasses import dataclass
from typing import List, Optional, Tuple

from ..parser.components import (
    CompositeTypeInfo, PreprocDefInfo,
    GlobalVariableInfo, FunctionInfo
)
from .code_editor import span_replace_many

def _r() -> str:
    return secrets.token_hex(1).upper()

Token = str
ReplRange = Tuple[int, int]  # (byte_start, byte_end)

@dataclass(frozen=True, slots=True)
class CodePlaceholder:
    token: Token
    original_code: str

    def to_json(self) -> dict:
        return {
            'token': self.token,
            'original_code': self.original_code,
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'CodePlaceholder':
        return cls(
            token=data['token'],
            original_code=data['original_code'],
        )
    

def placeholder_composition_type(
    cti: CompositeTypeInfo
) -> Optional[Tuple[ReplRange, Token]]:
    if cti.name is None:
        return None
    if (def_span := cti.definition_span) is None:
        return None

    # Only replace if the definition span is more than 3 lines
    def_start_row = def_span.start_point.row
    def_end_row = def_span.end_point.row
    if (def_end_row - def_start_row) < 3:
        return None

    replacement = f"_PH_{cti.name.upper()}_INIT_{_r()}_"

    # TODO: The definition_span should start from the opening brace '{'
    # and end at the closing brace '}',
    # This currently directly adjust the span without checking the actual braces.
    repl_range = (def_span.start_byte + 1,
                  def_span.end_byte - 1)

    return repl_range, replacement


def placeholder_preproc_def(
        pdti: PreprocDefInfo
) -> Optional[Tuple[ReplRange, Token]]:
    if pdti.name is None:
        return None
    if (arg_span := pdti.arg_span) is None:
        return None
    
    # Only replace if the argument span is more than 3 lines
    arg_start_row = arg_span.start_point.row
    arg_end_row = arg_span.end_point.row
    if (arg_end_row - arg_start_row) < 3:
        return None

    replacement = f"_PH_{pdti.name.upper()}_DEF_{_r()}_"
    repl_range = (arg_span.start_byte, arg_span.end_byte)

    return repl_range, replacement


def placeholder_global_variable(
        gvti: GlobalVariableInfo
) -> Optional[Tuple[ReplRange, Token]]:
    if gvti.name is None:
        return None
    if (init_span := gvti.init_list_span) is None:
        return None
    
    # Only replace if the initialization is more than 3 lines
    init_start_row = init_span.start_point.row
    init_end_row = init_span.end_point.row
    if (init_end_row - init_start_row) < 3:
        return None

    replacement = f"_PH_{gvti.name.upper()}_INIT_{_r()}_"

    # TODO: The init_list_span should start from the opening brace '{'
    # and end at the closing brace '}',
    # This currently directly adjust the span without checking the actual braces.
    repl_range = (init_span.start_byte + 1,
                  init_span.end_byte - 1)

    return repl_range, replacement


def placeholder_function(
        fti: FunctionInfo
) -> Optional[Tuple[ReplRange, Token]]:
    if fti.name is None:
        return None
    if (compound_span := fti.compound_span) is None:
        return None

    replacement = f"_PH_{fti.name.upper()}_BODY_{_r()}_"

    # TODO: The compound_span should start from the opening brace '{'
    # and end at the closing brace '}',
    # This currently directly adjust the span without checking the actual braces.
    repl_range = (compound_span.start_byte + 1,
                  compound_span.end_byte - 1)

    return repl_range, replacement


def replace_back_placeholder(
        source: bytes,
        placeholders: List[CodePlaceholder]
) -> bytes:
    if not placeholders:
        return source

    replacements: List[Tuple[ReplRange, Token]] = []

    for ph in placeholders:
        token_bytes = ph.token.encode('utf-8')
        begin, end = 0, len(source)
        while begin < end:
            idx = source.find(token_bytes, begin, end)
            if idx == -1:
                break
            repl_range = (idx, idx + len(ph.token))
            replacements.append((repl_range, ph.original_code))
            begin = idx + len(ph.token)

    replaced_bytes = span_replace_many(
        source,
        replacements
    )
    return replaced_bytes
