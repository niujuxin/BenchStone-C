from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple, NamedTuple

from ..parser.components import HasSourceSpan, GlobalVariableInfo
from ..csource import CSource
from .code_fingerprint import fingerprint_c
from .code_placeholder import CodePlaceholder, placeholder_global_variable
from .code_editor import span_replace


@dataclass(slots=True)
class ReferenceItem:
    location: Path
    source_snippet: str
    placeholder: Optional[CodePlaceholder] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> dict:
        return {
            'location': self.location.as_posix(),
            'source_snippet': self.source_snippet,
            'placeholder': self.placeholder.to_json() if self.placeholder else None,
            'metadata': self.metadata or None,
        }

    @classmethod
    def from_json(cls, data: dict) -> 'ReferenceItem':
        return cls(
            location=Path(data['location']),
            source_snippet=data['source_snippet'],
            placeholder=(
                CodePlaceholder.from_json(data['placeholder'])
                if data.get('placeholder') else None
            ),
            metadata=data.get('metadata') or {},
        )


class SymbolImplReference(NamedTuple):
    functions: list[ReferenceItem]
    function_declarations: list[ReferenceItem]
    global_variables: list[ReferenceItem]
    preproc_defs: list[ReferenceItem]
    composite_types: list[ReferenceItem]
    type_aliases: list[ReferenceItem]

    def _iter_items(self) -> Iterable[ReferenceItem]:
        yield from self.functions
        yield from self.function_declarations
        yield from self.global_variables
        yield from self.preproc_defs
        yield from self.composite_types
        yield from self.type_aliases

    def to_flattened_list(self) -> list[ReferenceItem]:
        return list(self._iter_items())

    def item_count(self) -> int:
        return (
            len(self.functions)
            + len(self.function_declarations)
            + len(self.global_variables)
            + len(self.preproc_defs)
            + len(self.composite_types)
            + len(self.type_aliases)
        )

    def is_empty(self) -> bool:
        return self.item_count() == 0

    def deterministic_resolve(self) -> Optional[Tuple[str, ReferenceItem]]:
        if self.item_count() != 1:
            return None

        ordered_categories = (
            ('preproc_def', self.preproc_defs),
            ('global_variable', self.global_variables),
            ('function', self.functions),
            ('composite_type', self.composite_types),
            ('type_alias', self.type_aliases),
        )

        for category, items in ordered_categories:
            if not items:
                continue
            reference = items[0]
            if category == 'global_variable':
                meta = reference.metadata
                if meta.get('is_extern'):
                    return None
                if not meta.get('has_initialize', True):
                    return None
            return category, reference

        return None


def prepare_symbol_reference(
    symbol_name: str,
    csource_dict: Mapping[Path, CSource],
    *,
    use_fingerprint: bool = True,
    use_code_placeholder: bool = True,
) -> SymbolImplReference:
    func_defs: list[ReferenceItem] = []
    func_decls: list[ReferenceItem] = []
    glob_vars: list[ReferenceItem] = []
    preproc_defs: list[ReferenceItem] = []
    composite_types: list[ReferenceItem] = []
    type_aliases: list[ReferenceItem] = []

    seen_fingerprints: set[str] = set()

    def _item(item: HasSourceSpan, cp: Path, cs: CSource) -> ReferenceItem:
        snippet = item.span.bytes_of(cs.as_bytes).decode("utf-8", errors="ignore").strip()
        return ReferenceItem(location=cp, source_snippet=snippet)

    def _item_glob_var(
        item: GlobalVariableInfo, cp: Path, cs: CSource
    ) -> ReferenceItem:
        metadata = {
            'is_extern': item.is_extern,
            'has_initialize': item.has_initialize,
        }

        just_return = not use_code_placeholder
        if not just_return:
            ph_info = placeholder_global_variable(item)
            just_return = ph_info is None

        if just_return:
            s = item.span.bytes_of(cs.as_bytes).decode(
                "utf-8", errors="ignore").strip()
            return ReferenceItem(
                location=cp,
                source_snippet=s,
                metadata=metadata,
            )

        else:
            repl_range, token = ph_info
            replaced_bytes = span_replace(cs.as_bytes, repl_range, token)
            s, e = repl_range
            placeholder = CodePlaceholder(
                token=token,
                original_code=cs.as_bytes[s:e].decode("utf-8", errors="ignore")
            )
            return ReferenceItem(
                location=cp,
                source_snippet=replaced_bytes.decode("utf-8", errors="ignore"),
                placeholder=placeholder,
                metadata=metadata,
            )

    def extend_if_new(
        candidates: Iterable[ReferenceItem],
        target_list: list[ReferenceItem],
    ) -> None:
        if not use_fingerprint:
            target_list.extend(candidates)
            return

        for candidate in candidates:
            snippet = candidate.source_snippet
            fingerprint = fingerprint_c(snippet)
            if fingerprint in seen_fingerprints:
                continue
            seen_fingerprints.add(fingerprint)
            target_list.append(candidate)

    for cp, cs in csource_dict.items():
        sr = cs.search_by_name(symbol_name)

        # Function
        extend_if_new((_item(func, cp, cs) for func in sr.functions), 
                      func_defs)
        # Global Variable
        extend_if_new(
            (_item_glob_var(gvar, cp, cs) for gvar in sr.global_variables),
            glob_vars,
        )
        # Function Declerator
        extend_if_new((_item(decl, cp, cs) for decl in sr.function_declerators), 
                      func_decls)
        # Preprocessor Definition
        extend_if_new((_item(pp, cp, cs) for pp in sr.preproc_defs), 
                      preproc_defs)
        # Composite Types
        extend_if_new(
            (
                _item(comp, cp, cs)
                for comp in sr.composite_types
                if not comp.is_forward_declaration()
            ),
            composite_types,
        )
        # Type Aliases
        extend_if_new((_item(alias, cp, cs) for alias in sr.type_aliases), 
                      type_aliases)

    return SymbolImplReference(
        functions=func_defs,
        function_declarations=[] if func_defs else func_decls,
        global_variables=glob_vars,
        preproc_defs=preproc_defs,
        composite_types=composite_types,
        type_aliases=[] if composite_types else type_aliases,
    )
