from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from src.csource.w_components import CSourceIncludes


C17_HEADERS = set([
    "assert.h", "complex.h", "ctype.h", "errno.h",
    "fenv.h", "float.h", "inttypes.h", "iso646.h",
    "limits.h", "locale.h", "math.h", "setjmp.h",
    "signal.h", "stdalign.h", "stdarg.h", "stdatomic.h",
    "stdbool.h", "stddef.h", "stdint.h", "stdio.h",
    "stdlib.h", "stdnoreturn.h", "string.h", "tgmath.h",
    "threads.h", "time.h", "uchar.h", "wchar.h",
    "wctype.h",
])
UNIX_SYS_HEADERS = set([
    "sys/types.h", "sys/stat.h", "sys/time.h",
    "sys/file.h", "syslog.h", "unistd.h",
])


def is_standard_header(include_name: str) -> bool:
    """Check if the include name is a standard C header."""
    normalized = include_name.lower()
    return (normalized in C17_HEADERS) or (normalized in UNIX_SYS_HEADERS)


def find_include_in_current_dir(
    include_name: str,
    from_file: Path | str,
    all_files: Iterable[Path | str]
) -> Optional[Path]:
    """
    Attempt to resolve the include relative to the including file's directory.
    Returns the resolved Path if it exists in `all_files`, otherwise None.
    """
    known_files = {Path(p) for p in all_files}
    source_path = Path(from_file).resolve()
    local_candidate = (source_path.parent / Path(include_name)).resolve()
    return local_candidate if local_candidate in known_files else None


def find_include_candidates(
    include_name: str,
    all_files: Iterable[Path | str]
) -> List[Path]:
    """
    Resolve candidate absolute paths for a (local) include directive.
    Try to match by normalized suffix components against `all_files`.
    Matching is case-insensitive, and the include string is normalized to remove
    '.' and resolve '..' segments.
    """
    known_files = {Path(p) for p in all_files}

    # Build normalized suffix parts

    suffix_parts: List[str] = []
    for part in Path(include_name).parts:
        if part in ("", "."):
            continue
        if part == "..":
            if suffix_parts:
                suffix_parts.pop()
            continue
        suffix_parts.append(part)

    if not suffix_parts:
        return []

    suffix_len = len(suffix_parts)
    suffix_lower = [part.lower() for part in suffix_parts]

    # Search for candidates

    candidates: List[Path] = []
    for candidate in known_files:
        if len(candidate.parts) < suffix_len:
            continue
        tail = candidate.parts[-suffix_len:]
        if [part.lower() for part in tail] == suffix_lower:
            candidates.append(candidate)

    return candidates


def determine_include_sources(
        target_include: str,
        from_file: Path | str,
        all_files: Iterable[Path | str]
) -> Tuple[bool, Optional[Path], List[Path]]:
    """
    Attempt to resolve an include directive to a specific file.

    Parameters
    ----------
    target_include:
        The include name as it appears in the source code (e.g. "myheader.h").
    from_file:
        The file (absolute or relative path) that contains the include directive.
    all_files:
        An iterable of all known files (absolute or relative paths).

    Returns
    -------
    is_standard: bool
        True if the include is a recognized standard header.
    local_path: Optional[Path]
        The resolved local include path if found; otherwise None.
    candidates: List[Path]
        A list of candidate paths that match the include name.
    """
    # If header has brackets or quotes, strip them
    target_include = target_include.strip()
    if (target_include.startswith('<') and target_include.endswith('>')) or \
       (target_include.startswith('"') and target_include.endswith('"')):
        target_include = target_include[1:-1].strip()

    if is_standard_header(target_include):
        return True, None, []

    local_path = find_include_in_current_dir(target_include, from_file, all_files)
    candidates = find_include_candidates(target_include, all_files)

    return False, local_path, candidates
