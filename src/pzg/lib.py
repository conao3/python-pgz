import pathlib


def create_repo_file(gitdir: pathlib.Path, filename: str) -> pathlib.Path:
    filepath = gitdir / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.touch()

    return filepath


def create_repo_dir(gitdir: pathlib.Path, dirname: str) -> pathlib.Path:
    dirpath = gitdir / dirname
    dirpath.mkdir(parents=True, exist_ok=True)

    return dirpath
