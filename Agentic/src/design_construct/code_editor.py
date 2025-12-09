
import re
from typing import Iterable, Tuple, Union

from ..parser.source_span import SourceSpan


SpanLike = Union[SourceSpan, Tuple[int, int]]
BytesLike = Union[str, bytes]


def span_replace(
        source: BytesLike,
        span: SpanLike,
        replacement: BytesLike
):
    if isinstance(source, str):
        source = source.encode('utf-8')
    if isinstance(replacement, str):
        replacement = replacement.encode('utf-8')
    
    if isinstance(span, SourceSpan):
        start_byte, end_byte = span.start_byte, span.end_byte
    else:
        start_byte, end_byte = span
    
    start_byte = max(0, min(len(source), start_byte))
    end_byte = max(start_byte, min(len(source), end_byte))
    return source[:start_byte] + replacement + source[end_byte:]


def span_remove(
        source: BytesLike,
        span: SpanLike
) -> BytesLike:
    return span_replace(source, span, b"")


def span_replace_many(
        source: BytesLike,
        spans: Iterable[Tuple[SpanLike, BytesLike]]
) -> BytesLike:
    source_was_text = isinstance(source, str)
    if source_was_text:
        source_bytes = source.encode("utf-8")
    else:
        source_bytes = source

    normalized: list[Tuple[int, int, bytes]] = []
    for span, replacement in spans:
        if isinstance(replacement, str):
            replacement_bytes = replacement.encode("utf-8")
        else:
            replacement_bytes = replacement

        if isinstance(span, SourceSpan):
            start_byte, end_byte = span.start_byte, span.end_byte
        else:
            start_byte, end_byte = span

        start_byte = max(0, min(len(source_bytes), start_byte))
        end_byte = max(start_byte, min(len(source_bytes), end_byte))
        normalized.append((start_byte, end_byte, replacement_bytes))

    normalized.sort(key=lambda item: item[0])

    chunks: list[bytes] = []
    last_index = 0
    for start_byte, end_byte, replacement_bytes in normalized:
        chunks.append(source_bytes[last_index:start_byte])
        chunks.append(replacement_bytes)
        last_index = end_byte

    chunks.append(source_bytes[last_index:])
    result_bytes = b"".join(chunks)

    if source_was_text:
        return result_bytes.decode("utf-8")
    return result_bytes


def span_remove_many(
        source: BytesLike,
        spans: Iterable[SpanLike]
) -> BytesLike:
    return span_replace_many(
        source,
        [(span, b"") for span in spans]
    )


def remove_excessive_newlines(source: BytesLike) -> BytesLike:
    """
    Replace sequences of more than two consecutive newlines with exactly two newlines.
    Preserves the type of the input (str or bytes).
    """
    if isinstance(source, str):
        return re.sub(r'\n{3,}', '\n\n', source)
    if isinstance(source, bytes):
        return re.sub(b'\n{3,}', b'\n\n', source)
    raise TypeError("source must be of type str or bytes")
