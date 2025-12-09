from __future__ import annotations

import hashlib
from tree_sitter import Node

from ..parser.tslang import get_parser, C_LANGUAGE

_parser = get_parser(C_LANGUAGE)


def _leaf_tokens(node: Node, buf: bytes):
    # Depth-first, left-to-right; comments/whitespace are "extras" and not part of the tree.
    if node.type in ("comment", "whitespace"):
        return
    if len(node.children) == 0:
        text = buf[node.start_byte:node.end_byte].decode("utf-8", errors="replace")
        if text.strip():  # drop any stray whitespace fragments
            yield text.strip()
        return
    for child in node.children:
        yield from _leaf_tokens(child, buf)


def normalize_c_to_tokens(source: str | bytes) -> list[str]:
    """
    Convert C source into a canonical sequence of lexical tokens:
    - ignores whitespace, newlines, comments
    - respects actual C token boundaries
    - preserves preprocessor directives as tokens
    - line continuations are spliced (ignored)
    """
    b = source.encode("utf-8") if isinstance(source, str) else source
    tree = _parser.parse(b)
    return list(_leaf_tokens(tree.root_node, b))


def normalize_c(source: str | bytes) -> str:
    """
    Canonical string form: tokens joined by a single space.
    Useful for diffing or hashing.
    """
    return " ".join(normalize_c_to_tokens(source))


def fingerprint_c(source: str | bytes) -> str:
    """
    Stable hash of the canonical form (for quick equality checks).
    """
    canon = normalize_c(source).encode("utf-8")
    return hashlib.sha256(canon).hexdigest()


if __name__ == "__main__":
    code1 = r"""
    #define MAX 10 
       // comment
    int f ( void ) {
        int x = \
        MAX;  /* block comment */
        return   x    ;
    }
    """

    code2 = r"""
    #define MAX 10
    int f(void){int x=MAX;return x;}
    """
    c1 = normalize_c(code1)
    c2 = normalize_c(code2)
    print("Normalized Code 1:", c1)
    print("Normalized Code 2:", c2)

    print("Fingerprint 1:", fingerprint_c(code1))
    print("Fingerprint 2:", fingerprint_c(code2))
    