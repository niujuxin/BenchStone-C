from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from src.design_construct.code_placeholder import CodePlaceholder

from .symbol_reference import ReferenceItem
from ..utils.run_cmd import CommandExecResult


@dataclass(slots=True, frozen=True)
class SourceBundle:
    """Container for source artifacts of a design snapshot."""
    c: str
    header: str
    main: Optional[str] = None

    @classmethod
    def initial_empty(
        cls,
        header_file_name: str = 'design.h',
    ) -> 'SourceBundle':
        return cls(
            c=f'#include "{header_file_name}"\n',
            header='', 
            main=None,
        )

    def to_json(self) -> dict:
        return {
            'c': self.c,
            'header': self.header,
            'main': self.main,
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'SourceBundle':
        return cls(
            c=data['c'],
            header=data['header'],
            main=data.get('main'),
        )

_EXCLUSIVE_SYMBOLS = (
    '__attribute__',
    '__declspec',
    '__cdecl',
    '__stdcall',
    '__thiscall',
    '__fastcall',
    '__vectorcall',
)

@dataclass(slots=True)
class Diagnostics:
    """Compile and symbol-resolution diagnostics for a design snapshot."""
    gcc_result: Optional[CommandExecResult]
    removed_forward_symbols: Tuple[str, ...]
    unresolved_symbols: Tuple[str, ...]
    llm_indicated_missing_symbols: Tuple[str, ...] = ()
    gcc_extra_incomplete_types: Tuple[str, ...] = ()

    @property
    def all_unresolved_symbols(self) -> Tuple[str, ...]:
        symbols = (set(self.removed_forward_symbols) |
                   set(self.unresolved_symbols) |
                   set(self.gcc_extra_incomplete_types) |
                   set(self.llm_indicated_missing_symbols))
        # Filter out exclusive symbols
        symbols = [s for s in symbols if s not in _EXCLUSIVE_SYMBOLS]
        return tuple(symbols)

    def to_json(self) -> dict:
        return {
            'gcc_result': self.gcc_result.to_json() if self.gcc_result else None,
            'removed_forward_symbols': self.removed_forward_symbols,
            'unresolved_symbols': self.unresolved_symbols,
            'gcc_extra_incomplete_types': self.gcc_extra_incomplete_types,
            'llm_indicated_missing_symbols': self.llm_indicated_missing_symbols,
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'Diagnostics':
        return cls(
            gcc_result=(CommandExecResult.from_json(data['gcc_result']) 
                        if data['gcc_result'] else None),
            removed_forward_symbols=tuple(data['removed_forward_symbols']),
            unresolved_symbols=tuple(data['unresolved_symbols']),
            gcc_extra_incomplete_types=tuple(data.get('gcc_extra_incomplete_types', ())),
            llm_indicated_missing_symbols=tuple(data.get('llm_indicated_missing_symbols', ())),
        )


@dataclass(slots=True, frozen=True)
class IncrementalConstructAttempt:
    """Details about an LLM-driven construction attempt."""
    references: Tuple[ReferenceItem, ...]
    llm_response_dumps: Optional[str]
    extracted_design: Optional[SourceBundle]
    llm_reported_missing_symbols: Tuple[str, ...] = ()
    llm_response_time_elapsed: Optional[float] = None

    def to_json(self) -> dict:
        return {
            'references': [ref.to_json() for ref in self.references],
            'llm_response_dumps': self.llm_response_dumps,
            'extracted_design': (self.extracted_design.to_json() 
                                 if self.extracted_design else None),
            'llm_reported_missing_symbols': self.llm_reported_missing_symbols,
            'llm_response_time_elapsed': self.llm_response_time_elapsed,
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'IncrementalConstructAttempt':
        return cls(
            references=tuple(ReferenceItem.from_json(ref) 
                             for ref in data.get('references', [])),
            llm_response_dumps=data.get('llm_response_dumps'),
            extracted_design=(SourceBundle.from_json(data['extracted_design']) 
                              if data.get('extracted_design') else None),
            llm_reported_missing_symbols=tuple(data.get('llm_reported_missing_symbols', ())),
            llm_response_time_elapsed=data.get('llm_response_time_elapsed'),
        )


@dataclass(slots=True, frozen=True)
class IncrementalConstructAttemptV2:
    """Details about an LLM-driven construction attempt."""
    references: dict[str, List[ReferenceItem]]
    llm_response_dumps: Optional[str]
    extracted_design: Optional[SourceBundle]
    llm_reported_missing_symbols: Tuple[str, ...] = ()
    llm_response_time_elapsed: Optional[float] = None

    def to_json(self) -> dict:
        return {
            'references': {k: [ref.to_json() for ref in v] for k, v in self.references.items()},
            'llm_response_dumps': self.llm_response_dumps,
            'extracted_design': (self.extracted_design.to_json() 
                                 if self.extracted_design else None),
            'llm_reported_missing_symbols': self.llm_reported_missing_symbols,
            'llm_response_time_elapsed': self.llm_response_time_elapsed,
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'IncrementalConstructAttemptV2':
        return cls(
            references={k: [ReferenceItem.from_json(ref) for ref in v] 
                        for k, v in data.get('references', {}).items()},
            llm_response_dumps=data.get('llm_response_dumps'),
            extracted_design=(SourceBundle.from_json(data['extracted_design']) 
                              if data.get('extracted_design') else None),
            llm_reported_missing_symbols=tuple(data.get('llm_reported_missing_symbols', ())),
            llm_response_time_elapsed=data.get('llm_response_time_elapsed'),
        )


@dataclass(slots=True)
class TraceStep:
    """Represents a single step in the construction trace."""
    uid: str
    #
    initial_design: SourceBundle
    diagnostic: Diagnostics
    target_symbols: Tuple[str, ...]
    attempt: IncrementalConstructAttemptV2

    # Following fields are optional
    placeholders: Optional[Tuple[CodePlaceholder]] = None

    # Following fields are for trace navigation
    # It is updated when adding new steps to the trace
    last_step: Optional[str] = None
    next_steps: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.uid:
            object.__setattr__(self, 'uid', str(uuid.uuid4()))

    @property
    def is_valid(self) -> bool:
        # Following situations indicate invalid step
        # 1. LLM failed to provide a design/ extracted_design is None
        if self.attempt.extracted_design is None:
            return False
        return True

    def to_json(self) -> dict:
        return {
            'uid': self.uid,
            #
            'initial_design': self.initial_design.to_json(),
            'diagnostic': self.diagnostic.to_json(),
            'target_symbols': self.target_symbols,
            'attempt': self.attempt.to_json(),
            #
            'placeholders': ([ph.to_json() for ph in self.placeholders] 
                             if self.placeholders is not None else None),
            #
            'last_step': self.last_step,
            'next_steps': self.next_steps,
        }

    @classmethod
    def from_json(cls, data: dict) -> 'TraceStep':
        return cls(
            uid=data['uid'],
            #
            initial_design=SourceBundle.from_json(data['initial_design']),
            diagnostic=Diagnostics.from_json(data['diagnostic']),
            target_symbols=tuple(data['target_symbols']),
            attempt=IncrementalConstructAttemptV2.from_json(data['attempt']),
            #
            placeholders=(tuple(CodePlaceholder.from_json(ph) 
                                for ph in data['placeholders']) 
                          if data.get('placeholders') else None),
            #
            last_step=data.get('last_step'),
            next_steps=data.get('next_steps', []),
        )

@dataclass(slots=True)
class DesignConstructTrace:
    """Full trace of incremental design construction."""
    steps: List[TraceStep] = field(default_factory=list)

    def sequential_valid_step_iter(self):
        root_step = None
        for step in self.steps:
            if step.last_step is None:
                root_step = step
                break
                
        if root_step is None:
            return
        
        current_step = root_step
        while current_step is not None:
            yield current_step
            next_steps = current_step.next_steps
            # For sequential trace, only one valid next step is expected
            if len(next_steps) > 1:
                raise ValueError("Multiple valid next steps found in "
                                 "sequential trace.")
            if not next_steps:
                break
            next_fingerprint = next_steps[0]
            current_step = self.find_step(next_fingerprint)

    def add_new_step(
            self, step: TraceStep, 
            parent_uid: Optional[str] = None
    ):
        # Update parent step's next_steps and set last_step of new step
        if parent_uid is not None:
            parent_step = self.find_step(parent_uid)
            if parent_step is None:
                raise ValueError(f"Parent step with fingerprint "
                                 f"{parent_uid} not found.")
            
            parent_step.next_steps.append(step.uid)
            step.last_step = parent_uid
        
        # Append the new step
        self.steps.append(step)

    def find_step(self, uid: str) -> Optional[TraceStep]:
        for step in self.steps:
            if step.uid == uid:
                return step
        return None

    def to_json(self) -> dict:
        return [
            step.to_json() for step in self.steps
        ]
    
    @classmethod
    def from_json(cls, data: dict) -> 'DesignConstructTrace':
        return cls(
            steps=[TraceStep.from_json(step_data) for step_data in data]
        )
    