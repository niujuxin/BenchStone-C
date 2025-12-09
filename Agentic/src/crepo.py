
from pathlib import Path
from typing import Iterator


class CRepo:
    ACCEPCT_EXTS = {
        # Common C source and header files
        ".c",
        ".h",
    }

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

        if not self.root.exists():
            raise FileNotFoundError(f"{self.root!s} does not exist")
        if not self.root.is_dir():
            raise NotADirectoryError(f"{self.root!s} is not a directory")

        files_all: list[Path] = []
        files_direct: list[Path] = []
        dirs_recursive: set[Path] = set()
        top_level_dirs: set[Path] = set()

        for path in self.root.rglob("*"):
            if not path.is_file():
                continue

            if path.suffix.lower() not in self.ACCEPCT_EXTS:
                continue

            files_all.append(path)
            dirs_recursive.add(path.parent)

            rel_parts = path.relative_to(self.root).parts

            if len(rel_parts) == 1:
                # File is directly under the repository root.
                files_direct.append(path)
                top_level_dirs.add(self.root)
            else:
                # File is within a subdirectory; capture that top-level directory.
                top_level_dirs.add(self.root / rel_parts[0])

        self._files_recursive: tuple[Path, ...] = tuple(sorted(files_all))
        self._files_non_recursive: tuple[Path, ...] = tuple(sorted(files_direct))
        self._dirs_recursive: tuple[Path, ...] = tuple(sorted(dirs_recursive))
        self._dirs_non_recursive: tuple[Path, ...] = tuple(sorted(top_level_dirs))

    def files(self, *, recursive: bool = True) -> list[Path]:
        if recursive:
            return list(self._files_recursive)
        else:
            return list(self._files_non_recursive)
    
    def dirs(self, *, recursive: bool = True) -> list[Path]:
        if recursive:
            return list(self._dirs_recursive)
        else:
            return list(self._dirs_non_recursive)

    def iter_files(self, *, recursive: bool = True) -> Iterator[Path]:
        if recursive:
            yield from self._files_recursive
        else:
            yield from self._files_non_recursive

    def iter_dirs(self, *, recursive: bool = True) -> Iterator[Path]:
        if recursive:
            yield from self._dirs_recursive
        else:
            yield from self._dirs_non_recursive

    def subrepo(self, *, recursive: bool = True) -> Iterator["CRepo"]:
        dirs = self._dirs_recursive if recursive else self._dirs_non_recursive

        for directory in dirs:
            if directory == self.root:
                continue
            yield CRepo(directory)


if __name__ == '__main__':

    from all_repos import REPO_ABSOLUTE_BASE, RepoPaths

    repo_root = REPO_ABSOLUTE_BASE / RepoPaths.FreeRTOS_Kernel

    repo = CRepo(repo_root)

    for fs in repo.iter_dirs(recursive=False):
        print(fs)

