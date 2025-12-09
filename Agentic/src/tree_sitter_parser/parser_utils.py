
from functools import lru_cache, wraps

import tree_sitter_c as tsc
from tree_sitter import Language, Parser


@lru_cache
def tree_sitter_c_parser() -> Parser:
    lang = Language(tsc.language())
    parser = Parser(lang)
    return parser


def byte2string(data: bytes) -> str:
    return data.decode("utf-8", errors="ignore")


def string2byte(data: str) -> bytes:
    return data.encode("utf-8", errors="ignore")


class ParserUnsuccessful(Exception): ...


def catch_parser_unsuccessful():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ParserUnsuccessful:
                return None
        return wrapper
    return decorator
