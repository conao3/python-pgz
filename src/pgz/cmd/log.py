from __future__ import annotations

import pathlib

import pydantic

from .. import lib
from .. import types
from .. import git_object


class Argument(pydantic.BaseModel):
    revision_range: str = 'HEAD'

    @classmethod
    def parse_args(cls, args_: list[str]) -> Argument:
        def help() -> None:
            print('''\
log: Show commit logs.

Usage: pgz log [options...] [<revision range>]

Arguments:
    <revision range>    Specify the revision range.

Options:
    -h, --help    Show this message and exit.
''')

        obj = cls()
        args: list[str] = []

        while args_:
            arg = args_.pop(0)
            if arg == '--':
                args.extend(args_)
                break
            elif arg in ('-h', '--help'):
                help()
                exit(0)
            elif arg.startswith('-'):
                raise Exception(f'Unknown option: {arg}')
            else:
                args.append(arg)

        if len(args) == 1:
            obj.revision_range = args[0]
        else:
            raise Exception('Invalid arguments')

        return obj


def main_log_1(gitdir: pathlib.Path, sha: str, seen: list[str]) -> None:
    obj = git_object.from_sha(gitdir, sha)
    if not isinstance(obj, types.GitObjectCommit):
        raise Exception(f'Not a commit: {sha}')

    print(f'commit {sha} -> {obj.parent}')

    if obj.parent and not obj.parent in seen:
        seen.append(obj.parent)
        main_log_1(gitdir, obj.parent, seen)


def main_log(args_: list[str]) -> None:
    args = Argument.parse_args(args_)

    gitdir = lib.locate_dominating_file(pathlib.Path.cwd(), '.git')
    if not gitdir:
        raise Exception('Not a git repository')

    main_log_1(gitdir, args.revision_range, [])
