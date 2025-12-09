
from dataclasses import dataclass
from typing import Optional
from tree_sitter import Node

from ..utils import children_of_type, iter_tree
from ..source_span import SourceSpan


@dataclass(frozen=True)
class PreprocDefInfo:
    span: SourceSpan
    name: Optional[str] = None
    params_span: Optional[SourceSpan] = None
    arg_span: Optional[SourceSpan] = None
    
    def to_json(self) -> dict:
        return {
            'span': self.span.to_json(),
            'name': self.name,
            'params_span': self.params_span.to_json() if self.params_span else None,
            'arg_span': self.arg_span.to_json() if self.arg_span else None
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'PreprocDefInfo':
        return cls(
            span=SourceSpan.from_json(data['span']),
            name=data.get('name'),
            params_span=SourceSpan.from_json(data['params_span']) if data.get('params_span') else None,
            arg_span=SourceSpan.from_json(data['arg_span']) if data.get('arg_span') else None
        )
    
    def __str__(self) -> str:
        return (f"PreprocDefInfo(name={self.name}, span={self.span}, "
                f"params_span={self.params_span}, arg_span={self.arg_span})")
    
    def __repr__(self) -> str:
        return (f"PreprocDefInfo(name={self.name!r}, span={self.span!r}, "
                f"params_span={self.params_span!r}, arg_span={self.arg_span!r})")



def extract_preproc_defs(root: 'Node', source: bytes) -> list[PreprocDefInfo]:

    results: list[PreprocDefInfo] = []

    for node in iter_tree(root):
        if node.type in {'preproc_def', 'preproc_function_def'}:
            
            identifier = children_of_type(node, {'identifier'})
            identifier = identifier[0] if identifier else None
            if identifier:
                name = identifier.text.decode('utf-8', errors='replace')
            else:
                name = None
            
            arg = children_of_type(node, {'preproc_arg', })
            arg_span = None
            if arg:
                arg_span = SourceSpan.from_node(arg[0])
            
            params = children_of_type(node, {'preproc_params', })
            params_span = None
            if params:
                params_span = SourceSpan.from_node(params[0])

            results.append(PreprocDefInfo(
                span=SourceSpan.from_node(node),
                name=name,
                params_span=params_span,
                arg_span=arg_span
            ))

    return results
