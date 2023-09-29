from __future__ import annotations

import pathlib
import sys
from typing import Optional

import pydantic

from .. import lib
from .. import types
from .. import git_object


class Argument(pydantic.BaseModel):
    type: Optional[types.GitObjectTypeEnum] = None
    object: Optional[str] = None

    @classmethod
    def parse_args(cls, args_: list[str]) -> Argument:
        def help() -> None:
            print('''\
cat-file: Provide content or type and size information for repository objects.

Usage: pgz cat-file [options...] <type> <object>

Arguments:
    <type>      Specify the type.  (commit, tree, tag, blob)
    <object>    Specify the object.

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

        if len(args) != 2:
            raise Exception(f'Expected 2 arguments, got {len(args)}')

        type_, obj.object = args

        enum_type = types.GitObjectTypeEnum.from_str(type_)
        if not enum_type:
            raise Exception(f'Unknown type: {type_}')

        obj.type = enum_type

        return obj


def main_cat_file(args_: list[str]) -> None:
    args = Argument.parse_args(args_)

    gitdir = lib.locate_dominating_file(pathlib.Path.cwd(), '.git')
    if not gitdir:
        raise Exception('Not a git repository')

    obj = git_object.from_sha(gitdir, args.type, args.object)
    sys.stdout.buffer.write(obj.data)
