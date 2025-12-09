

from dataclasses import dataclass
from typing import List, Literal

from tree_sitter import Node

from ..source_span import SourceSpan
from ..utils import iter_tree, str_of


@dataclass(frozen=True)
class CommentInfo:
    style: Literal["line", "block", "doc", "unknown"]
    span: SourceSpan
    
    def to_json(self) -> dict:
        return {
            'style': self.style,
            'span': self.span.to_json()
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'CommentInfo':
        return cls(
            style=data['style'],
            span=SourceSpan.from_json(data['span'])
        )
    
    def __str__(self) -> str:
        return f"CommentInfo(style={self.style}, span={self.span})"
    
    def __repr__(self) -> str:
        return (f"CommentInfo(style={self.style!r}, "
                f"span={self.span!r})")


def extract_comments(root: Node, source: bytes) -> List[CommentInfo]:
    out: List[CommentInfo] = []
    for n in iter_tree(root, named_only=False):
        if n.type == "comment":
            txt = str_of(n, source)
            style: Literal["line", "block", "doc", "unknown"]
            if txt.startswith("///") or txt.startswith("//!") or txt.startswith("/**"):
                style = "doc"
            elif txt.startswith("//"):
                style = "line"
            elif txt.startswith("/*"):
                style = "block"
            else:
                style = "unknown"
            out.append(CommentInfo(style=style, span=SourceSpan.from_node(n)))
    return out
