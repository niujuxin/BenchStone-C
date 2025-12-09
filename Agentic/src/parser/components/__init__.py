
from typing import Protocol

from ..source_span import SourceSpan


class HasSourceSpan(Protocol):
    span: SourceSpan


from .comment import extract_comments, CommentInfo
from .conditional import extract_conditionals, ConditionalMacroInfo
from .function import extract_functions, FunctionInfo
from .include import extract_includes, IncludeInfo
from .glob_declerator import extract_global_declerators, GlobalVariableInfo, FunctionDecleratorInfo
from .type_alias import extract_type_aliases, TypeAlias
from .composite_type import extract_composite_types, CompositeTypeInfo
from .preproc_def import extract_preproc_defs, PreprocDefInfo
