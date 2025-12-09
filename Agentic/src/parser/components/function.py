
import re
from dataclasses import dataclass
from typing import List, Optional
from tree_sitter import Node

from ..source_span import SourceSpan

from ..utils import children_of_type, descendants_of_type, str_of, iter_tree


@dataclass(frozen=True)
class FunctionInfo:
    """Function declaration or definition."""
    name: Optional[str]                  
    span: SourceSpan                            # declaration/definition statement span
    signature: Optional[str] = None             # best-effort full signature text
    compound_span: Optional[SourceSpan] = None  # body span for definitions
    
    def to_json(self) -> dict:
        return {
            'name': self.name,
            'span': self.span.to_json(),
            'signature': self.signature,
            'compound_span': (self.compound_span.to_json()
                              if self.compound_span else None),
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'FunctionInfo':
        return cls(
            name=data.get('name'),
            span=SourceSpan.from_json(data['span']),
            signature=data.get('signature'),
            compound_span=(SourceSpan.from_json(data['compound_span'])
                           if data.get('compound_span') else None),
        )
    
    def __str__(self) -> str:
        return (f"FunctionInfo(name={self.name}, '{self.signature}', "
                f"span={self.span}, compound_span={self.compound_span})")

    def __repr__(self) -> str:
        return (f"FunctionInfo(name={self.name!r}, signature={self.signature!r}, "
                f"span={self.span!r}, compound_span={self.compound_span!r})")


def extract_functions(root: Node, source: bytes) -> List[FunctionInfo]:
    out: List[FunctionInfo] = []
    
    def _extract(def_node: Node) -> Optional[FunctionInfo]:
        decl_node = children_of_type(
            def_node, {'pointer_declarator', 'function_declarator'}
        )
        decl_node = decl_node[0] if decl_node else None

        identifier = descendants_of_type(
            decl_node, {'identifier', }
        )
        name = str_of(identifier[0], source) if identifier else None

        compound_node = children_of_type(
            def_node, {'compound_statement', }
        )
        compound_node = compound_node[0] if compound_node else None
        
        # Signature is the full text from beginning of definition
        # to the beginning of the compound statement
        if decl_node and compound_node:
            signature_start = def_node.start_byte
            signature_end = compound_node.start_byte
            signature = source[signature_start:signature_end].decode('utf-8', errors='ignore')
            # Remove all newlines and excessive spaces
            signature = re.sub(r'\s+', ' ', signature).strip()
        else:
            signature = None

        return FunctionInfo(
            name=name,
            span=SourceSpan.from_node(def_node),
            signature=signature,
            compound_span=SourceSpan.from_node(compound_node) if compound_node else None,
        )

    # 1) Definitions
    for def_node in iter_tree(root, named_only=True):
        if def_node.type == 'function_definition':
            
            try:
                func_info = _extract(def_node)
                if func_info:
                    out.append(func_info)
            except Exception as e:
                # Ignore extraction errors
                continue

    # Sort by source order
    out.sort(key=lambda f: f.span.start_byte)
    return out
