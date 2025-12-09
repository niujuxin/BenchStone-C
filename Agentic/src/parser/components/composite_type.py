

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Set

from tree_sitter import Node

from ..utils import descendants_of_type, is_under, iter_tree, str_of
from ..source_span import SourceSpan


@dataclass(frozen=True)
class CompositeTypeInfo:
    kind: Literal["struct", "union", "enum"]
    name: Optional[str]                   # type name, None if anonymous, best effort
    span: SourceSpan                      # span of the specifier/declaration
    definition_span: Optional[SourceSpan] = None  # span of the full definition
                                                  # `field_declaration_list` for struct/union,
                                                  # `enumerator_list` for enum

    def is_anonymous(self) -> bool:
        return self.name is None
    
    def is_forward_declaration(self) -> bool:
        return self.definition_span is None

    def to_json(self) -> dict:
        return {
            'kind': self.kind,
            'name': self.name,
            'span': self.span.to_json(),
            'definition_span': (self.definition_span.to_json() 
                                if self.definition_span else None),
        }   
    
    @classmethod
    def from_json(cls, data: dict) -> 'CompositeTypeInfo':
        return cls(
            kind=data['kind'],
            name=data.get('name'),
            span=SourceSpan.from_json(data['span']),
            definition_span=(SourceSpan.from_json(data['definition_span']) 
                             if data.get('definition_span') else None)
        )
    
    def __str__(self) -> str:
        return (f"CompositeTypeInfo(kind={self.kind}, name={self.name}, "
                f"span={self.span}, definition_span={self.definition_span})")
    
    def __repr__(self) -> str:
        return (
            f"CompositeTypeInfo(kind={self.kind!r}, name={self.name!r}, "
            f"span={self.span!r}, definition_span={self.definition_span!r})")


_SPECIFIER_NODE_KINDS: Dict[str, str] = {
    "struct_specifier": "struct",
    "union_specifier":  "union",
    "enum_specifier":   "enum",
}

_DEFINITION_NODE_KINDS: Set[str] = {
    "field_declaration_list",
    "enumerator_list",
}

def extract_composite_types(
        root: Node, source: bytes,
        *,
        ignore_forward_declarations: bool = False,
        ignore_anonymous: bool = False
) -> List[CompositeTypeInfo]:
    out: List[CompositeTypeInfo] = []

    for n in iter_tree(root, named_only=True):
        if n.type in _SPECIFIER_NODE_KINDS:
            kind = _SPECIFIER_NODE_KINDS[n.type]

            # Remove if under function parameter/body, variable declarator
            if is_under(n, {
                "function_definition", 
                "declaration",
            }):
                continue

            name = _extract_type_name_from_specifier(n, source)
            if name is None and ignore_anonymous:
                continue

            definition_node = _search_definition(n)
            if definition_node is None and ignore_forward_declarations:
                continue
            field_decl_span = (SourceSpan.from_node(definition_node) 
                               if definition_node else None)
            
            # If the node is under `field_declaration`
            # and the definition_node is None, it means it's a forward declaration
            # inside another struct/union used as a type of a field.
            # This should be ignored.
            # NOTE: This is not affected by the `ignore_forward_declarations` flag
            if is_under(n, {"field_declaration", }) and definition_node is None:
                continue
            
            out.append(CompositeTypeInfo(
                kind=kind,
                name=name,
                span=SourceSpan.from_node(n),
                definition_span=field_decl_span
            ))

    out.sort(key=lambda t: t.span.start_byte)
    return out


def _search_definition(spec: Node) -> Optional[Node]:
    for ch in spec.children:
        if ch.type in _DEFINITION_NODE_KINDS:
            return ch
    return None


def _extract_type_name_from_specifier(spec: Node, source: bytes) -> Optional[str]:
    # Try common child node types that carry names
    for ch in spec.children:
        if ch.type == 'type_identifier':
            return str_of(ch, source).strip()
    # Some specs put name deeper; search
    for n in descendants_of_type(spec, {"type_identifier", }):
        # Avoid names that are part of base classes or fields
        if is_under(n, _DEFINITION_NODE_KINDS):
            continue
        return str_of(n, source).strip()
    # Could be anonymous
    return None
