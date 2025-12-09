from typing import List
from tree_sitter import Node, Point

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class SourceSpan:
    """A source span with byte range and point range (0-based line/column)."""
    start_byte: int
    end_byte: int
    start_point: Point
    end_point: Point

    def bytes_of(self, source_bytes: bytes | str) -> bytes:
        """Extract the text corresponding to this span from the source bytes."""
        if isinstance(source_bytes, str):
            source_bytes = source_bytes.encode('utf-8', errors='ignore')
        return source_bytes[self.start_byte:self.end_byte]

    def str_of(self, source_str: bytes | str) -> str:
        """Extract the text corresponding to this span from the source string."""
        if isinstance(source_str, str):
            source_str = source_str.encode('utf-8', errors='ignore')
        return source_str[self.start_byte:self.end_byte].decode('utf-8', errors='ignore')

    def to_json(self) -> dict:
        return {
            'start_byte': self.start_byte,
            'end_byte': self.end_byte,
            'start_point': {
                'row': self.start_point.row,
                'column': self.start_point.column
            },
            'end_point': {
                'row': self.end_point.row,
                'column': self.end_point.column
            }
        }

    @classmethod
    def from_json(cls, data: dict) -> 'SourceSpan':
        """Create a SourceSpan from a JSON dictionary."""
        start_point = Point(
            row=data['start_point']['row'],
            column=data['start_point']['column']
        )
        end_point = Point(
            row=data['end_point']['row'],
            column=data['end_point']['column']
        )

        return cls(
            start_byte=data['start_byte'],
            end_byte=data['end_byte'],
            start_point=start_point,
            end_point=end_point
        )

    def __str__(self) -> str:
        # Add 1 to row/column for human-friendly 1-based display
        start_point_str = f"({self.start_point.row+1},{self.start_point.column+1})"
        end_point_str = f"({self.end_point.row+1},{self.end_point.column+1})"
        return (f"Span[{start_point_str},{end_point_str}]")

    def __repr__(self) -> str:
        return (f"SourceSpan(byte_range=({self.start_byte}, {self.end_byte}), "
                f"point_range=({self.start_point}, {self.end_point}))")

    @classmethod
    def from_node(cls, node: Node) -> 'SourceSpan':
        return cls(
            start_byte=node.start_byte,
            end_byte=node.end_byte,
            start_point=node.start_point,
            end_point=node.end_point,
        )
    

def source_span_insides(inner: SourceSpan, outer: SourceSpan) -> bool:
    """Check if the inner SourceSpan is completely inside the outer SourceSpan."""
    return (outer.start_byte <= inner.start_byte and
            outer.end_byte >= inner.end_byte)


def source_span_overlaps(s1: SourceSpan, s2: SourceSpan) -> bool:
    """Check if two SourceSpans overlap."""
    return not (s1.end_byte <= s2.start_byte or 
                s2.end_byte <= s1.start_byte)


def _max_point(a: Point, b: Point) -> Point:
    
    def _point_coords(point: Point) -> tuple[int, int]:
        """Extract (row, column) from a Point-like object."""
        if hasattr(point, "row"):
            return point.row, point.column
        # Fallback for tuple-like points
        return point[0], point[1]

    a_row, a_col = _point_coords(a)
    b_row, b_col = _point_coords(b)

    if (a_row, a_col) >= (b_row, b_col):
        return a
    return b


def merge_spans(spans: List[SourceSpan]) -> List[SourceSpan]:
    if not spans:
        return []

    # Sort spans by start position so we can sweep from left to right.
    ordered = sorted(spans, key=lambda span: (span.start_byte, span.end_byte))

    merged: List[SourceSpan] = []
    current = ordered[0]

    for span in ordered[1:]:
        if current.end_byte >= span.start_byte:  # Overlap or adjacency
            # Extend the current span to cover the new one.
            # NOTE: Suppose point and byte are consistent. No need to check.
            new_end_byte = max(current.end_byte, span.end_byte)
            new_end_point = _max_point(current.end_point, span.end_point)
            current = replace(current, end_byte=new_end_byte, end_point=new_end_point)
        else:
            merged.append(current)
            current = span

    merged.append(current)
    return merged
