
from tree_sitter import Parser, Language, Query, QueryCursor, Tree

import tree_sitter_cpp as tscpp
import tree_sitter_c as tsc


C_LANGUAGE = Language(tsc.language())
CPP_LANGUAGE = Language(tscpp.language())


def get_qcursor(
        query_src: str,
        *,
        lang: Language,
        source_byte_range: tuple[int, int] = None,
) -> QueryCursor:
    query = Query(lang, query_src)
    cursor = QueryCursor()
    if source_byte_range is not None:
        cursor.set_byte_range(*source_byte_range)
    return cursor


def get_parser(lang: Language) -> Parser:
    parser = Parser(lang)
    return parser


def parse_c_source(source: bytes) -> Tree:
    parser = get_parser(C_LANGUAGE)
    return parser.parse(source)
