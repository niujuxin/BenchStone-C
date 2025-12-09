
from typing import Iterable, List, Optional, Union

from tree_sitter import Node


def byte_of(node: Node, source: bytes) -> bytes:
    return source[node.start_byte:node.end_byte]


def str_of(node: Node, source: bytes) -> str:
    return byte_of(node, source).decode('utf-8', errors='replace')


def iter_tree(root: Node, named_only: bool = False) -> Iterable[Node]:
    """Pre-order DFS over the whole tree."""
    stack = [root]
    while stack:
        n = stack.pop()
        yield n
        children = n.named_children if named_only else n.children
        # Reverse for stable pre-order
        for c in reversed(children):
            stack.append(c)


def is_under(node: Node, ancestor_types: set[str]) -> bool:
    p = node.parent
    while p is not None:
        if p.type in ancestor_types:
            return True
        p = p.parent
    return False


def nearest_ancestor(node: Node, types: set[str]) -> Optional[Node]:
    p = node.parent
    while p is not None:
        if p.type in types:
            return p
        p = p.parent
    return None


def descendants_of_type(node: Node, types: set[str]) -> List[Node]:
    return [n for n in iter_tree(node, named_only=False) if (n is not node and n.type in types)]


def children_of_type(node: Node, types: set[str]) -> List[Node]:
    return [n for n in node.children if n.type in types]


def directive_header_text(node: Node, source: bytes) -> str:
    """
    Extract the full header line(s) of a preprocessor directive, handling line continuations.
    If a \ is found at the end of a line, the next line is included as well.
    """
    start = node.start_byte
    limit = node.end_byte
    cursor = start
    segments: List[bytes] = []

    while cursor < limit:
        newline = source.find(b'\n', cursor, limit)
        if newline == -1:
            newline = limit

        line = source[cursor:newline]
        stripped_right = line.rstrip()
        continued = stripped_right.endswith(b'\\')

        if continued:
            stripped_right = stripped_right[:-1].rstrip()

        if segments:
            segments.append(stripped_right.lstrip())
        else:
            segments.append(stripped_right.lstrip())

        cursor = newline + 1
        if not continued:
            break

    if not segments:
        return ""

    header_bytes = b' '.join(part for part in segments if part)
    return header_bytes.decode("utf-8", errors="replace")


def find_nodes_outside_types(
    root: Node,
    target_types: Union[str, Iterable[str]],
    disqualifying_types: Optional[Iterable[str]] = None,
) -> List[Node]:
    """
    Return every node whose ``node.type`` is in ``target_types`` and which does not
    have any ancestor whose ``type`` appears in ``disqualifying_types``.

    Parameters
    ----------
    root:
        The root ``tree_sitter.Node`` (typically the translation unit / module node).
    target_types:
        Either a single node.type string or an iterable of node.type strings that
        identify the nodes you want to collect.
    disqualifying_types:
        Optional iterable of node.type strings.  If a candidate node has an ancestor
        whose ``type`` is in this collection, that candidate is excluded.  If omitted,
        an empty set is assumed (no ancestors disqualify).

    Returns
    -------
    List[Node]
        All matching nodes that are not nested inside any disqualifying construct.
    """
    if isinstance(target_types, str):
        target_types = {target_types}
    else:
        target_types = set(target_types)

    if disqualifying_types is None:
        disqualifying_types = set()
    else:
        disqualifying_types = set(disqualifying_types)

    def has_disqualifying_ancestor(node: Node) -> bool:
        ancestor = node.parent
        while ancestor is not None:
            if ancestor.type in disqualifying_types:
                return True
            ancestor = ancestor.parent
        return False

    results: List[Node] = []
    stack: List[Node] = [root]

    while stack:
        current = stack.pop()

        if current.type in target_types and not has_disqualifying_ancestor(current):
            results.append(current)

        # Maintain source order by pushing children in reverse.
        stack.extend(reversed(current.children))

    return results
