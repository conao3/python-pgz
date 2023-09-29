from __future__ import annotations

import configparser
import pathlib

import pydantic

from .. import lib


def repo_default_config() -> configparser.ConfigParser:
    config_parser = configparser.ConfigParser()

    config_parser.add_section('core')
    config_parser.set('core', 'repositoryformatversion', '0')
    config_parser.set('core', 'filemode', 'false')
    config_parser.set('core', 'bare', 'false')

    return config_parser


class Argument(pydantic.BaseModel):
    @classmethod
    def parse_args(cls, args_: list[str]) -> Argument:
        return cls()


def main_init(args_: list[str]) -> None:
    _arg = Argument.parse_args(args_)

    worktree = pathlib.Path.cwd()
    gitdir = worktree / '.git'

    if gitdir.exists():
        raise Exception(f'Already exists .git repository: {gitdir}')

    lib.create_repo_dir(gitdir, 'branches')
    lib.create_repo_dir(gitdir, 'objects')
    lib.create_repo_dir(gitdir, 'refs/tags')
    lib.create_repo_dir(gitdir, 'refs/heads')

    with lib.create_repo_file(gitdir, 'description').open('w') as f:
        f.write("Unnamed repository; edit this file 'description' to name the repository.\n")

    with lib.create_repo_file(gitdir, 'HEAD').open('w') as f:
        f.write('ref: refs/heads/master\n')

    with lib.create_repo_file(gitdir, 'config').open('w') as f:
        config_parser = repo_default_config()
        config_parser.write(f)
