
from dataclasses import dataclass
from typing import List, Optional, Tuple

from tree_sitter import Node

from ..source_span import SourceSpan
from ..utils import children_of_type, descendants_of_type, find_nodes_outside_types


@dataclass(frozen=True)
class FunctionDecleratorInfo:
    span: SourceSpan
    name: Optional[str]

    def to_json(self) -> dict:
        return {
            'span': self.span.to_json(),
            'name': self.name,
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'FunctionDecleratorInfo':
        return cls(
            span=SourceSpan.from_json(data['span']),
            name=data.get('name'),
        )
    
    def __str__(self) -> str:
        return f"FunctionDecleratorInfo(name={self.name}, span={self.span})"
    
    def __repr__(self) -> str:
        return (f"FunctionDecleratorInfo(name={self.name!r}, "
                f"span={self.span!r})")


@dataclass(frozen=True)
class GlobalVariableInfo:
    span: SourceSpan
    name: Optional[str]
    is_extern: bool
    is_static: bool
    has_initialize: bool

    # This is specifically the span of the initializer list
    # for array or struct initializations, if any.
    # The initializer list is something embraced in curly braces,
    # for example: int arr[] = {1, 2, 3};
    init_list_span: Optional[SourceSpan] = None

    def to_json(self) -> dict:
        return {
            'span': self.span.to_json(),
            'name': self.name,
            'is_extern': self.is_extern,
            'is_static': self.is_static,
            'has_initialize': self.has_initialize,
            'init_list_span': (self.init_list_span.to_json()
                                if self.init_list_span else None),
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'GlobalVariableInfo':
        return cls(
            span=SourceSpan.from_json(data['span']),
            name=data.get('name'),
            is_extern=data['is_extern'],
            is_static=data['is_static'],
            has_initialize=data['has_initialize'],
            init_list_span=(SourceSpan.from_json(data['init_list_span'])
                              if data.get('init_list_span') else None),
        )
    
    def storage_keywords(self) -> List[str]:
        keywords = []
        if self.is_extern:
            keywords.append("extern")
        if self.is_static:
            keywords.append("static")
        return keywords

    def __str__(self) -> str:
        return (f"GlobalVariableInfo(name={self.name}, "
                f"extern={self.is_extern}, static={self.is_static}, "
                f"has_initialize={self.has_initialize}, "
                f"span={self.span}, init_list={self.init_list_span})")

    def __repr__(self) -> str:
        return (f"GlobalVariableInfo(name={self.name!r}, "
                f"extern={self.is_extern!r}, static={self.is_static!r}, "
                f"has_initialize={self.has_initialize!r}, "
                f"span={self.span!r}, init_list={self.init_list_span!r})")


def _extract_global_declerators(
        root: Node,
        source: bytes,
) -> List[FunctionDecleratorInfo | GlobalVariableInfo]:
    
    declerators = find_nodes_outside_types(
        root,
        target_types="declaration",
        disqualifying_types={
            "function_definition",
            "compound_statement",
            "field_declaration_list",
        }
    )

    results: List[FunctionDecleratorInfo | GlobalVariableInfo] = []

    def _extract_function_declerator(n: Node) -> FunctionDecleratorInfo | None:
        function_declerator = descendants_of_type(n, {"function_declarator", })
        if not function_declerator: 
            return None
        function_declerator = function_declerator[0]
        identifier = children_of_type(function_declerator, {"identifier", })
        identifier = identifier[0] if identifier else None
        if identifier:
            name = source[identifier.start_byte:identifier.end_byte].decode("utf-8")
        else:
            name = None
        return FunctionDecleratorInfo(
            name=name,
            span=SourceSpan.from_node(n),
        )

    def _extract_global_variable(n: Node) -> GlobalVariableInfo | None:
        storage_class_specifiers = children_of_type(n, {
            "storage_class_specifier",
        })
        is_extern = any(
            source[scs.start_byte:scs.end_byte] == b"extern"
            for scs in storage_class_specifiers
        )
        is_static = any(
            source[scs.start_byte:scs.end_byte] == b"static"
            for scs in storage_class_specifiers
        )

        init_declerator = children_of_type(n, {"init_declarator", })
        init_declerator = init_declerator[0] if init_declerator else None
        
        identifier_under: Node = n
        if init_declerator:
            identifier_under = init_declerator

        identifier = descendants_of_type(identifier_under, {"identifier", })
        identifier = identifier[0] if identifier else None

        if identifier:
            name = source[identifier.start_byte:identifier.end_byte].decode("utf-8")
        else:
            name = None
        
        init_list_node = None
        if init_declerator:
            init_list_node = children_of_type(
                init_declerator,
                {"initializer_list", },
            )
            if init_list_node:
                init_list_node = init_list_node[0]

        return GlobalVariableInfo(
            name=name,
            span=SourceSpan.from_node(n),
            is_extern=is_extern,
            is_static=is_static,
            has_initialize=bool(init_declerator),
            init_list_span=SourceSpan.from_node(init_list_node) if init_list_node else None,
        )

    for declaration in declerators:
        
        result = (
            # Only if function declerator failed then try global variable
            _extract_function_declerator(declaration) or
            _extract_global_variable(declaration)
        )
        if result is not None:
            results.append(result)

    return results


def extract_global_declerators(
        root: Node,
        source: bytes,
) -> Tuple[List[FunctionDecleratorInfo], List[GlobalVariableInfo]]:
    declerators = _extract_global_declerators(root, source)
    functions: List[FunctionDecleratorInfo] = []
    global_vars: List[GlobalVariableInfo] = []

    for d in declerators:
        if isinstance(d, FunctionDecleratorInfo):
            functions.append(d)
        elif isinstance(d, GlobalVariableInfo):
            global_vars.append(d)

    return functions, global_vars
