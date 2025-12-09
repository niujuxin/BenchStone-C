from functools import cached_property
from typing import Optional, Union

from tree_sitter import Node

from ..parser.tslang import C_LANGUAGE, get_parser
from ..parser.utils import str_of



class PureCSource:
    def __init__(self, source: Union[str, bytes]) -> None:
        if isinstance(source, bytes):
            self._bytes: Optional[bytes] = source
            self._str: Optional[str] = None
        else:
            self._str = source
            self._bytes = None

    @cached_property
    def as_bytes(self) -> bytes:
        cached = self._bytes
        if cached is None:
            cached = self._str.encode("utf-8")
            self._bytes = cached
        return cached

    @cached_property
    def as_str(self) -> str:
        cached = self._str
        if cached is None:
            cached = self._bytes.decode("utf-8", errors="replace")
            self._str = cached
        return cached

    @cached_property
    def lines(self) -> tuple[str]:
        return tuple(self.as_str.splitlines())
        
    def slice_bytes(self, start: int, end: int) -> bytes:
        return self.as_bytes()[start:end]

    def slice_text(self, start: int, end: int) -> str:
        return self.as_str()[start:end]


class CSourceAST(PureCSource):
    def __init__(self, source: Union[str, bytes]) -> None:
        super().__init__(source)
        parser = get_parser(C_LANGUAGE)
        self.tree = parser.parse(self.as_bytes)
        self.root = self.tree.root_node

    def print_ast(self, node: Node = None, indent: int = 0):
        if node is None:
            node = self.tree.root_node
        indent_str = "  " * indent
        node_text = str_of(node, self.as_bytes)
        desp = f"{indent_str}{node.type} [{node.start_byte} - {node.end_byte}] : {node_text!r}"
        print(desp)

        for child in node.children:
            self.print_ast(child, indent + 1)
        pass