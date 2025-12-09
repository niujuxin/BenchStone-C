from collections import defaultdict

from ..parser.source_span import SourceSpan, merge_spans
from ..csource.csource import CSource
from .code_editor import remove_excessive_newlines, span_remove_many
from .forward_decl_find import find_forward_decls


def remove_forward_decls(
        sources: list[CSource]
) -> tuple[list[str], list[CSource]]:
    labeled_sources = [(str(idx), csource) 
                       for idx, csource in enumerate(sources)]
    forward_decls = find_forward_decls(labeled_sources)

    replaced_spans: dict[str, list[SourceSpan]] = defaultdict(list)
    for occurrences in forward_decls.values():
        for occ in occurrences:
            replaced_spans[occ.source_label].append(occ.span)

    removed_symbols = list(forward_decls.keys())

    new_sources: list[CSource] = []
    for idx, csource in enumerate(sources):
        label = str(idx)
        spans = replaced_spans.get(label, [])
        merged_spans = merge_spans(spans)

        new_source = span_remove_many(
            csource.as_bytes,
            merged_spans
        )
        new_source = remove_excessive_newlines(new_source)
        new_sources.append(CSource(new_source))

    return removed_symbols, new_sources


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input",
        type=str,
        required=True,
        nargs='+',
        help="Path to the input C source file."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        help=("Dir to the output C source file with forward declerations removed. "
              "If the file exists, it will be overwritten.")
    )
    args = parser.parse_args()

    sources = [CSource.from_file(input_fp) for input_fp in args.input]

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    removed_symbols, new_sources = remove_forward_decls(sources)

    print("Removed forward declerations for symbols:")
    for sym in removed_symbols:
        print(f" - {sym}")

    for input_fp, new_csource in zip(args.input, new_sources):
        output_fp = output_dir / Path(input_fp).name
        with open(output_fp, 'wb') as f:
            f.write(new_csource.as_bytes)
        print(f"Wrote modified source to: {output_fp}")