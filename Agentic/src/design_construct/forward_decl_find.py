from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

from ..parser.source_span import SourceSpan
from ..csource import CSource


@dataclass(frozen=True)
class ForwardDeclOccurrence:
    """
    Represents a forward placeholder occurrence, tying a span to its source label.
    """
    source_label: str
    span: SourceSpan


ForwardDeclMap = Dict[str, List[ForwardDeclOccurrence]]
LabeledCSource = Tuple[str, CSource]


class ForwardDeclFinder:
    """
    Finds forward declarations (functions and composite types) across a set of labeled C sources
    and reports the source label for each occurrence. The order of occurrences is preserved based
    on the order of the provided sources.
    """

    def __init__(self, labeled_csources: Iterable[LabeledCSource]):
        self._labeled_csources: List[LabeledCSource] = list(labeled_csources)

    def find(self) -> ForwardDeclMap:
        """
        Return a mapping of symbols that were declared but never defined, along with the list
        of occurrences (source label + span) for each symbol.
        """
        forward_decls: defaultdict[str, List[ForwardDeclOccurrence]] = defaultdict(list)

        self._merge_results(
            forward_decls,
            self._find_function_forward_decls()
        )
        self._merge_results(
            forward_decls,
            self._find_composite_type_forward_decls()
        )

        return dict(forward_decls)

    def _find_function_forward_decls(self) -> ForwardDeclMap:
        """
        Collect function declarations that never receive a definition across all sources.
        """
        declarations: defaultdict[str, List[ForwardDeclOccurrence]] = defaultdict(list)
        definitions: set[str] = set()

        for source_label, csource in self._labeled_csources:
            for func in csource.functions:
                if func.compound_span is None:
                    declarations[func.name].append(
                        ForwardDeclOccurrence(source_label, func.span)
                    )
                else:
                    definitions.add(func.name)

            for func_decl in csource.function_declerators:
                declarations[func_decl.name].append(
                    ForwardDeclOccurrence(source_label, func_decl.span)
                )

        return {
            name: occurrences
            for name, occurrences in declarations.items()
            if name not in definitions
        }

    def _find_composite_type_forward_decls(self) -> ForwardDeclMap:
        """
        Collect composite types (struct/union/enum) that remain forward declarations.
        """
        decls: defaultdict[str, List[ForwardDeclOccurrence]] = defaultdict(list)
        defined_types: set[str] = set()

        for source_label, csource in self._labeled_csources:
            for comp_type in csource.composite_types:
                if comp_type.is_anonymous():
                    continue

                if comp_type.is_forward_declaration():
                    decls[comp_type.name].append(
                        ForwardDeclOccurrence(source_label, comp_type.span)
                    )
                else:
                    defined_types.add(comp_type.name)

        for defined in defined_types:
            decls.pop(defined, None)

        return dict(decls)

    def _merge_results(
        self,
        aggregate: defaultdict[str, List[ForwardDeclOccurrence]],
        fragment: ForwardDeclMap
    ) -> None:
        for name, occurrences in fragment.items():
            aggregate[name].extend(occurrences)


def find_forward_decls(
    labeled_csources: Iterable[LabeledCSource],
) -> ForwardDeclMap:
    """
    Convenience function to match the previous module-level API.
    """
    finder = ForwardDeclFinder(labeled_csources)
    return finder.find()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "csource_fps",
        type=str,
        nargs="+",
        help="Paths to the C source files to analyze."
    )
    args = parser.parse_args()

    csources: Sequence[CSource] = [CSource.from_file(fp) for fp in args.csource_fps]
    labeled_csources: List[LabeledCSource] = list(zip(args.csource_fps, csources))

    finder = ForwardDeclFinder(labeled_csources)
    forward_decls = finder.find()

    for name, occurrences in forward_decls.items():
        print(f"Forward declerations for '{name}':")
        for occurrence in occurrences:
            print(f"  - {occurrence.source_label}: {occurrence.span}")
            