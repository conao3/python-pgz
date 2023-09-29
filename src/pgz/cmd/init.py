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
        def help() -> None:
            print('''\
init: Initialize a new, empty repository.

Usage: pgz init [options...]

Options:
    -h, --help    Show this message and exit.
''')

        obj = cls()
        args: list[str] = []

        while args_:
            arg = args_.pop(0)
            if arg in ('-h', '--help'):
                help()
                exit(0)
            elif arg.startswith('-'):
                raise Exception(f'Unknown option: {arg}')
            else:
                args.append(arg)

        if len(args) != 0:
            raise Exception(f'Unknown arguments: {args}')

        return obj


def main_init(args_: list[str]) -> None:
    _arg = Argument.parse_args(args_)

    worktree = pathlib.Path.cwd()
    gitdir = worktree / '.git'

    if gitdir.exists():
        raise Exception(f'Already exists .git repository: {gitdir}')

    lib.get_or_create_repo_dir(gitdir, 'branches')
    lib.get_or_create_repo_dir(gitdir, 'objects')
    lib.get_or_create_repo_dir(gitdir, 'refs/tags')
    lib.get_or_create_repo_dir(gitdir, 'refs/heads')

    with lib.get_or_create_repo_file(gitdir, 'description').open('w') as f:
        f.write("Unnamed repository; edit this file 'description' to name the repository.\n")

    with lib.get_or_create_repo_file(gitdir, 'HEAD').open('w') as f:
        f.write('ref: refs/heads/master\n')

    with lib.get_or_create_repo_file(gitdir, 'config').open('w') as f:
        config_parser = repo_default_config()
        config_parser.write(f)
