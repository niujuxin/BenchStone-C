from __future__ import annotations

from collections import defaultdict
from typing import Mapping, Sequence

from .symbol_reference import ReferenceItem, SymbolImplReference

# (categories_with_same_priority, max_items_to_return)
_PRIORITY_LEVELS: tuple[tuple[Sequence[str], int | None], ...] = (
    (('preproc_def', 'global_variable', 'type_alias'), None),
    (('function',), 2),
    (('composite_type', 'type_alias'), 2),
)


def heuristic_next_target_symbols(
    sym_ref_map: Mapping[str, SymbolImplReference],
) -> list[tuple[str, list[ReferenceItem]]]:
    
    deterministic_by_category: dict[str, list[tuple[str, ReferenceItem]]] = defaultdict(list)
    non_deterministic: list[tuple[str, SymbolImplReference]] = []
    no_ref_symbols: list[str] = []

    for sym_name, sym_ref in sym_ref_map.items():
        # Skip symbols with no references
        if sym_ref.item_count() == 0:
            no_ref_symbols.append(sym_name)
            continue

        # Check for deterministic resolution
        resolved = sym_ref.deterministic_resolve()
        if resolved is None:
            non_deterministic.append((sym_name, sym_ref))
            continue
        category, reference = resolved
        deterministic_by_category[category].append((sym_name, reference))

    candidates = []

    # Add all preprocessor definitions, global variables
    for cat in ('preproc_def', 'global_variable'):
        items = deterministic_by_category.get(cat)
        for name, ref in items or ():
            candidates.append((name, [ref]))  # NOTE: Wrap ref in a list to match return type
    
    # Add composite types and type aliases last
    for cat in ('composite_type', 'type_alias'):
        items = deterministic_by_category.get(cat)
        for name, ref in items or ():
            candidates.append((name, [ref]))  # NOTE: Wrap ref in a list to match return type

    # Add all functions next
    for name, ref in deterministic_by_category.get('function', ()):
        candidates.append((name, [ref]))  # NOTE: Wrap ref in a list to match return type
    
    if candidates:
        return candidates
    
    # Select one non-deterministic symbol with the fewest references
    if non_deterministic:
        target_name, target_ref = min(non_deterministic, key=lambda item: item[1].item_count())
        return [(target_name, target_ref.to_flattened_list())]

    # Only no-reference symbols remain
    # Directly return them all
    return [(name, []) for name in no_ref_symbols]
