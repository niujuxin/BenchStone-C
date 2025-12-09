
import re
from dataclasses import dataclass
from typing import List, Optional

from tree_sitter import Node

from ..source_span import SourceSpan

from ..utils import iter_tree, str_of


@dataclass(frozen=True)
class IncludeInfo:
    span: SourceSpan
    include_target: Optional[str] = None
    
    def to_json(self) -> dict:
        return {
            'span': self.span.to_json(),
            'include_target': self.include_target
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'IncludeInfo':
        return cls(
            span=SourceSpan.from_json(data['span']),
            include_target=data.get('include_target')
        )
    
    def __str__(self) -> str:
        target = f"{self.include_target}" if self.include_target else ""
        return f"IncludeInfo({target}, span={self.span})"
    
    def __repr__(self) -> str:
        return (f"IncludeInfo(span={self.span!r}, "
                f"include_target={self.include_target!r})")
    

_INCLUDE_RE = re.compile(r'#\s*include\s*(?P<path><[^>]+>|"[^"]+")')

_SIGNIFICANT_PREPROC_TYPES = {"preproc_include"}


def extract_includes(root: Node, source: bytes) -> List[IncludeInfo]:
    results: List[IncludeInfo] = []
    for node in iter_tree(root, named_only=False):
        if node.type not in _SIGNIFICANT_PREPROC_TYPES:
            continue
        text = str_of(node, source).strip()
        match = _INCLUDE_RE.match(text)
        if not match:
            continue
        results.append(
            IncludeInfo(
                span=SourceSpan.from_node(node),
                include_target=match.group("path"),
            )
        )
    results.sort(key=lambda info: info.span.start_byte)
    return results
