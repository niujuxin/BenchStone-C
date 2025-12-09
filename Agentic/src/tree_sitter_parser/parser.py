
from typing import List
from tree_sitter import Node

from .parser_utils import (
    catch_parser_unsuccessful,
    string2byte, byte2string,
    ParserUnsuccessful
)


@catch_parser_unsuccessful
def parse_preproc_def(
        root: Node
):
    ...


@catch_parser_unsuccessful
def parse_preproc_function_def(
        root: Node
):
    ...


def parse_translation_unit(
        root: Node
):
    assert root.type == 'translation_unit'

    """Pre-order DFS over the whole tree."""
    stack = [root]
    while stack:
        n = stack.pop()
        
        if n.type == 'preproc_def':
            parse_preproc_def(n)
        elif n.type == 'preproc_function_def':
            parse_preproc_function_def(n)

        # If a node has already been processed by a subroutine, 
        # all its child nodes are ignored and not searched deeper.
        else:
            children = n.children
            # Reverse for stable pre-order
            for c in reversed(children):
                stack.append(c)
