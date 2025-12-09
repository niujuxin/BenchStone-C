from dataclasses import dataclass
import re
from typing import List, Pattern
from pathlib import Path
import tempfile

from requests_cache import Optional

from ..utils.run_cmd import CommandRunner


class _SymbolType:
    IMPLICIT_FUNC = 'implicit_func'
    UNKNOWN_TYPE = 'unknown_type'
    UNDECLARED = 'undeclared'
    UNDEFINED_REFERENCE = 'undefined_reference'
    INVALID_INCOMPLETE_TYPEDEF = 'invalid_incomplete_typedef'
    INVALID_USE_UNDEF_TYPE = 'invalid_use_undef_type'


_MappingTypeToErrorLog = {
    _SymbolType.IMPLICIT_FUNC: 'implicit declaration of function',
    _SymbolType.UNKNOWN_TYPE: 'unknown type name',
    _SymbolType.UNDECLARED: 'undeclared',
    _SymbolType.UNDEFINED_REFERENCE: 'undefined reference',
    _SymbolType.INVALID_INCOMPLETE_TYPEDEF: 'invalid use of incomplete typedef',
    _SymbolType.INVALID_USE_UNDEF_TYPE: 'invalid use of undefined type',
}


@dataclass(frozen=True)
class UnresolvedSymbol:
    symbol: str
    type: str
    filename: str = ''
    line: int = -1
    column: int = -1

    def title(self) -> str:
        return f"{self.symbol}: {_MappingTypeToErrorLog.get(self.type, 'unknown error')}"
        

def gcc_compile(
        c_file_name: str, c_contents: str, 
        h_file_name: str, h_contents: str,
        use_math_h: bool = False,
):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        (tmpdir / c_file_name).write_text(c_contents)
        (tmpdir / h_file_name).write_text(h_contents)

        command = ['gcc', c_file_name]
        if use_math_h:
            command.append('-lm')

        rlt = CommandRunner.run(
            command=command,
            workingdir=tmpdir.as_posix()
        )

    return rlt


@dataclass(frozen=True)
class _PatternSpec:
    symbol_type: str
    regex: Pattern[str]


_PATTERN_SPECS: List[_PatternSpec] = [
    _PatternSpec(
        symbol_type=_SymbolType.IMPLICIT_FUNC,
        regex=re.compile(
            r"^(?P<filename>.*?):(?P<line>\d+):(?P<column>\d+):\s*warning\s*:\s*implicit declaration of function\s*[`'‘’](?P<symbol>[^`'‘’]+)[`'‘’]",
            re.MULTILINE,
        ),
    ),
    _PatternSpec(
        symbol_type=_SymbolType.UNKNOWN_TYPE,
        regex=re.compile(
            r"^(?P<filename>.*?):(?P<line>\d+):(?P<column>\d+):\s*error\s*:\s*unknown type name\s*[`'‘’](?P<symbol>[^`'‘’]+)[`'‘’]",
            re.MULTILINE,
        ),
    ),
    _PatternSpec(
        symbol_type=_SymbolType.UNDECLARED,
        regex=re.compile(
            r"^(?P<filename>.*?):(?P<line>\d+):(?P<column>\d+):\s*error\s*:\s*[`'‘’](?P<symbol>[^`'‘’]+)[`'‘’]\s*undeclared",
            re.MULTILINE,
        ),
    ),
    _PatternSpec(
        symbol_type=_SymbolType.UNDEFINED_REFERENCE,
        regex=re.compile(
            r"^(?P<filename>.+?):\(.+?\):\s*undefined reference to\s*[`'‘’](?P<symbol>[^`'‘’]+)[`'‘’]",
            re.MULTILINE,
        ),
    ),
    _PatternSpec(
        symbol_type=_SymbolType.INVALID_INCOMPLETE_TYPEDEF,
        regex=re.compile(
            r"^(?P<filename>.*?):(?P<line>\d+):(?P<column>\d+):\s*error\s*:\s*invalid use of incomplete typedef\s*[`'‘’](?P<symbol>[^`'‘’]+)[`'‘’]",
            re.MULTILINE,
        ),
    ),
    _PatternSpec(
        symbol_type=_SymbolType.INVALID_USE_UNDEF_TYPE,
        regex=re.compile(
            r"^(?P<filename>.*?):(?P<line>\d+):(?P<column>\d+):\s*error\s*:\s*invalid use of undefined type\s*[`'‘’](?P<symbol>[^`'‘’]+)[`'‘’]",
            re.MULTILINE,
        ),
    ),
]


def _to_int(value: Optional[str]) -> Optional[int]:
    return int(value) if value is not None else None


def parse_gcc_unresolved_symbol(error_log: str) -> List[UnresolvedSymbol]:
    seen = set()
    unresolved: List[UnresolvedSymbol] = []

    for spec in _PATTERN_SPECS:
        for match in spec.regex.finditer(error_log):
            symbol = match.group("symbol")
            key = (spec.symbol_type, symbol)
            if key in seen:
                continue

            seen.add(key)
            unresolved.append(
                UnresolvedSymbol(
                    type=spec.symbol_type,
                    filename=match.group("filename"),
                    line=_to_int(match.groupdict().get("line")),
                    column=_to_int(match.groupdict().get("column")),
                    symbol=symbol,
                )
            )

    return unresolved