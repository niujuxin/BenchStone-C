from collections import deque
from pathlib import Path
from typing import Dict, Sequence, Set, Tuple

from ..include_resolve import determine_include_sources
from ..csource import CSource


def collect_include_dependencies(
    root: Path,
    all_repo_files: Sequence[Path],
    sources: Dict[Path, CSource],
) -> Tuple[Set[str], Dict[Path, CSource]]:
    """
    Walk the include graph starting at ``root`` and collect:
      * The set of unique standard-library include targets encountered.
      * The mapping of repository-local translation units that are reachable
        from ``root`` via include directives.

    Parameters
    ----------
    root:
        Entry translation unit for the traversal.
    all_repo_files:
        Repository files that can satisfy non-standard include directives.
    sources:
        Mapping from translation unit paths to parsed ``CSource`` objects.

    Returns
    -------
    tuple[set[str], dict[Path, CSource]]
        A pair consisting of the discovered standard include targets and a
        dictionary of resolved translation units.

    Raises
    ------
    KeyError
        If ``root`` or any reachable file is not present in ``sources``.
    """
    queue = deque([root])
    discovered: Set[Path] = {root}
    visited: Set[Path] = set()

    std_includes: Set[str] = set()
    resolved_sources: Dict[Path, CSource] = {}

    while queue:
        current_path = queue.pop()
        if current_path in visited:
            continue
        visited.add(current_path)

        current_csource = sources[current_path]
        resolved_sources[current_path] = current_csource

        for include_info in current_csource.includes:
            is_std, local, candidates = determine_include_sources(
                include_info.include_target,
                current_path,
                all_repo_files,
            )

            if is_std:
                std_includes.add(include_info.include_target)
                continue

            next_paths = (local,) if local is not None else candidates
            for next_path in next_paths:
                if next_path not in discovered:
                    queue.append(next_path)
                    discovered.add(next_path)

    return std_includes, resolved_sources
