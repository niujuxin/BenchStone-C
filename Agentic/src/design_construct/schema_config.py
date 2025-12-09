from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Tuple


@dataclass(slots=True, frozen=True)
class DesignMetaInfo:
    """Top-level metadata for a design trace."""
    repo_name: str
    design_name: str
    type: Literal['horizontal', 'vertical']
    top_functions: Tuple[str, ...] = ()
    entry_files: Tuple[Path] = ()

    def to_json(self) -> dict:
        return {
            'repo_name': self.repo_name,
            'design_name': self.design_name,
            'type': self.type,
            'top_functions': self.top_functions,
            'entry_files': [p.as_posix() for p in self.entry_files],
        }

    @classmethod
    def from_json(cls, data: dict) -> 'DesignMetaInfo':
        return cls(
            repo_name=data['repo_name'],
            design_name=data['design_name'],
            type=data['type'],
            top_functions=tuple(data.get('top_functions', ())),
            entry_files=tuple(Path(p) for p in data.get('entry_files', ())),
        )
    

@dataclass(slots=True, frozen=True)
class DesignMetaV2:
    """Top-level metadata for a design trace (version 2)."""
    function_location: Path
    function_name: str
    granularity: Literal['primitive', 'routine', 'workflow', 'end_to_end_scenario']
    logic_type: Literal['computation', 'control', 'data_processing', 'algorithm']
