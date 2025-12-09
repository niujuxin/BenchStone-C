
import re
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional

from tree_sitter import Node

from ..source_span import SourceSpan
from ..utils import iter_tree, directive_header_text


@dataclass(frozen=True)
class ConditionalMacroInfo:
    kind: Literal["if", "ifdef", "ifndef", "elif", "else", "endif"]
    span: SourceSpan
    
    # TODO: Change them to SourceSpan.
    name: Optional[str] = None
    condition: Optional[str] = None
    
    def to_json(self) -> dict:
        return {
            'kind': self.kind,
            'span': self.span.to_json(),
            'name': self.name,
            'condition': self.condition
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'ConditionalMacroInfo':
        return cls(
            kind=data['kind'],
            span=SourceSpan.from_json(data['span']),
            name=data.get('name'),
            condition=data.get('condition')
        )
    
    def __str__(self) -> str:
        return (f"ConditionalMacroInfo(kind={self.kind}, span={self.span}, "
                f"name={self.name}, condition={self.condition})")
    
    def __repr__(self) -> str:
        return (f"ConditionalMacroInfo(kind={self.kind!r}, span={self.span!r}, "
                f"name={self.name!r}, condition={self.condition!r})")


_CONDITION_REGEX: Dict[str, re.Pattern[str]] = {
    "if": re.compile(r'#\s*if\s+(?P<expr>.+)$', flags=re.S),
    "ifdef": re.compile(r'#\s*ifdef\s+(?P<name>[A-Za-z_]\w*)'),
    "ifndef": re.compile(r'#\s*ifndef\s+(?P<name>[A-Za-z_]\w*)'),
    "elif": re.compile(r'#\s*elif\s+(?P<expr>.+)$', flags=re.S),
}

_SIGNIFICANT_PREPROC_TYPES = {
    "preproc_if",
    "preproc_ifdef",
    "preproc_elif",
    "preproc_else",
}

def extract_conditionals(root: Node, source: bytes) -> List[ConditionalMacroInfo]:
    results: List[ConditionalMacroInfo] = []
    for node in iter_tree(root, named_only=False):
        if node.type not in _SIGNIFICANT_PREPROC_TYPES:
            continue

        # Get the full directive header text when line continuations are used
        header_text = directive_header_text(node, source)
        if not header_text:
            continue

        if node.type == "preproc_else":
            results.append(ConditionalMacroInfo(kind='else', span=SourceSpan.from_node(node)))
        
        elif node.type == 'preproc_ifdef':
            # `preproc_ifdef` is used for both `#ifdef` and `#ifndef`
            ifdef_match = _CONDITION_REGEX['ifdef'].match(header_text)
            ifndef_match = _CONDITION_REGEX['ifndef'].match(header_text)

            if ifdef_match or ifndef_match:
                results.append(
                    ConditionalMacroInfo(
                        kind='ifdef' if ifdef_match else 'ifndef',
                        span=SourceSpan.from_node(node),
                        name=(ifdef_match or ifndef_match).group("name"),
                    )
                )
        
        elif node.type == 'preproc_if' or node.type == 'preproc_elif':
            kind = 'if' if node.type == 'preproc_if' else 'elif'
            match = _CONDITION_REGEX['if'].match(header_text)
            if match:
                results.append(
                    ConditionalMacroInfo(
                        kind=kind,
                        span=SourceSpan.from_node(node),
                        condition=match.group("expr").strip(),
                    )
                )

    results.sort(key=lambda info: info.span.start_byte)
    return results
