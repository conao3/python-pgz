import pathlib
from typing import Optional


def create_repo_file(gitdir: pathlib.Path, filename: str) -> pathlib.Path:
    filepath = gitdir / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.touch()

    return filepath


def create_repo_dir(gitdir: pathlib.Path, dirname: str) -> pathlib.Path:
    dirpath = gitdir / dirname
    dirpath.mkdir(parents=True, exist_ok=True)

    return dirpath


def locate_dominating_file(path: pathlib.Path, filename: str) -> Optional[pathlib.Path]:
    path = path.resolve()

    while not (path / filename).exists():
        if path.parent == path:
            return None
        path = path.parent

    return path / filename
