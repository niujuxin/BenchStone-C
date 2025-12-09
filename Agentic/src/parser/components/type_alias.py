
from dataclasses import dataclass
from typing import List, Literal

from requests_cache import Optional
from tree_sitter import Node

from ..source_span import SourceSpan
from ..utils import descendants_of_type, iter_tree, str_of


@dataclass(frozen=True)
class TypeAlias:
    kind: Literal["typedef"]
    name: Optional[str]           # alias name
    span: SourceSpan              # span of the specifier/declaration
    
    def to_json(self) -> dict:
        return {
            'kind': self.kind,
            'name': self.name,
            'span': self.span.to_json(),
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'TypeAlias':
        return cls(
            kind=data['kind'],
            name=data.get('name'),
            span=SourceSpan.from_json(data['span']),
        )
    
    def __str__(self) -> str:
        return (f"TypeAlias(kind={self.kind}, name={self.name}, span={self.span})")
    
    def __repr__(self) -> str:
        return (f"TypeAlias(kind={self.kind!r}, name={self.name!r}, "
                f"span={self.span!r})")


def extract_type_aliases(root: Node, source: bytes) -> List[TypeAlias]:
    out: List[TypeAlias] = []

    for n in iter_tree(root, named_only=True):
        # C 'typedef'
        if n.type == "type_definition":
            out.append(_extract_typedef(n, source))

    out.sort(key=lambda t: t.span.start_byte)
    return out


def _extract_typedef(n: Node, source: bytes) -> TypeAlias:
    """
    Extract alias names for C 'type_definition' nodes.
    """
    node_text = str_of(n, source).strip()

    # TODO: Improve alias name extraction
    # Heuristic: name is the last identifier, 
    # pick the last type_identifier(s) before ';'
    alias_names_nodes = descendants_of_type(n, {"type_identifier", })

    last_node: Optional[Node] = None
    last_start_byte = -1
    for an in alias_names_nodes:
        if an.start_byte > last_start_byte:
            last_node = an
            last_start_byte = an.start_byte

    return TypeAlias(
        kind="typedef",
        name=str_of(last_node, source).strip() if last_node else None,
        span=SourceSpan.from_node(n),
    )
