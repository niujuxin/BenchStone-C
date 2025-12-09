from src.csource.w_components import CSourceComponents


from pathlib import Path


class CSource(CSourceComponents):

    @classmethod
    def from_file(cls, filepath: str | bytes | Path) -> "CSource":
        with open(filepath, 'rb') as f:
            source_bytes = f.read()
        return cls(source_bytes)
    