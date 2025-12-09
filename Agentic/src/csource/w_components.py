from typing import NamedTuple, Union

from .base import CSourceAST
from ..parser.components import (
    extract_comments,
    extract_conditionals,
    extract_functions, FunctionInfo,
    extract_includes,
    extract_global_declerators, GlobalVariableInfo, FunctionDecleratorInfo,
    extract_type_aliases, TypeAlias,
    extract_composite_types, CompositeTypeInfo,
    extract_preproc_defs, PreprocDefInfo,
)


class CSourceComments(CSourceAST):
    def __init__(self, source: Union[str, bytes]) -> None:
        super().__init__(source)
        self.comments = tuple(extract_comments(self.root, self.as_bytes))


class CSourceConditionals(CSourceAST):
    def __init__(self, source: Union[str, bytes]) -> None:
        super().__init__(source)
        self.conditionals = tuple(extract_conditionals(self.root, self.as_bytes))
        

class CSourceIncludes(CSourceAST):
    def __init__(self, source: Union[str, bytes]) -> None:
        super().__init__(source)
        self.includes = tuple(extract_includes(self.root, self.as_bytes))


class SymbolSearchResult(NamedTuple):
    functions: list[FunctionInfo]
    function_declerators: list[FunctionDecleratorInfo]
    global_variables: list[GlobalVariableInfo]
    preproc_defs: list[PreprocDefInfo]
    composite_types: list[CompositeTypeInfo]
    type_aliases: list[TypeAlias]


_EXCLUSIVE_SYMBOLS = (
    '__attribute__',
    '__declspec',
    '__cdecl',
    '__stdcall',
    '__thiscall',
    '__fastcall',
    '__vectorcall',
)

class CSourceComponents(CSourceComments, CSourceConditionals, CSourceIncludes):
    def __init__(self, source: Union[str, bytes]) -> None:
        super().__init__(source)

        self.functions = tuple(
            fd 
            for fd in extract_functions(self.root, self.as_bytes)
            if fd.compound_span is not None
        )
        self.type_aliases = tuple(extract_type_aliases(self.root, self.as_bytes))
        self.composite_types = tuple(extract_composite_types(
            self.root, self.as_bytes,
            ignore_anonymous=False,
            ignore_forward_declarations=False,
        ))
        _func_decl, _glob_var = extract_global_declerators(self.root, self.as_bytes)
        self.function_declerators = tuple(_func_decl)
        self.global_variables = tuple(_glob_var)
        self.preproc_defs = tuple(extract_preproc_defs(self.root, self.as_bytes))

    def search_by_name(
            self, name: str,
    ):
        if name in _EXCLUSIVE_SYMBOLS:
            return SymbolSearchResult(
                functions=[],
                function_declerators=[],
                global_variables=[],
                preproc_defs=[],
                composite_types=[],
                type_aliases=[]
            )
        
        # Functions
        funcs = [func for func in self.functions if func.name == name]
        func_decls = [decl for decl in self.function_declerators 
                      if decl.name == name]
        
        # Variables
        vars_ = [var for var in self.global_variables if var.name == name]

        # Preproc defines
        defines = [define for define in self.preproc_defs 
                   if define.name == name]
        
        # Composite types
        name_parts = name.split()
        name = ' '.join(p for p in name_parts if p not in ('struct', 'union', 'enum'))
        composites = [comp for comp in self.composite_types if comp.name == name]
        
        # Type aliases
        aliases = [alias for alias in self.type_aliases 
                   if alias.name == name]
        
        return SymbolSearchResult(
            functions=funcs,
            function_declerators=func_decls,
            global_variables=vars_,
            preproc_defs=defines,
            composite_types=composites,
            type_aliases=aliases
        )
