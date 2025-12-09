from dataclasses import dataclass, field
from typing import List


@dataclass
class HorizontalKernel:
    name: str
    src: List[str]
    base_dir: str
    top_functions: List[str] = field(default_factory=list)