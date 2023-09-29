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
    pretty: bool = False
    show_type: bool = False

    @classmethod
    def parse_args(cls, args_: list[str]) -> Argument:
        def help() -> None:
            print('''\
cat-file: Provide content or type and size information for repository objects.

Usage: pgz cat-file [options...] <type> <object>
       pgz cat-file (-e | -p) <object>
       pgz cat-file (-t | -s) <object>

Arguments:
    <type>      Specify the type.  (commit, tree, tag, blob)
    <object>    Specify the object.

Options:
    -p            Pretty-print the contents of <object> based on its type.
    -t            Instead of the content, show the object type identified by <object>.
    -h, --help    Show this message and exit.
''')

        obj = cls()
        args: list[str] = []

        while args_:
            arg = args_.pop(0)
            if arg == '--':
                args.extend(args_)
                break
            elif arg == '-p':
                obj.pretty = True
            elif arg == '-t':
                obj.show_type = True
            elif arg in ('-h', '--help'):
                help()
                exit(0)
            elif arg.startswith('-'):
                raise Exception(f'Unknown option: {arg}')
            else:
                args.append(arg)

        if len(args) == 2:
            type_, obj.object = args

            enum_type = types.GitObjectTypeEnum.from_str(type_)
            if not enum_type:
                raise Exception(f'Unknown type: {type_}')

            obj.type = enum_type
        elif len(args) == 1:
            obj.object = args[0]
        else:
            raise Exception(f'Expected 1 or 2 arguments, got {args}')

        return obj


def main_cat_file(args_: list[str]) -> None:
    args = Argument.parse_args(args_)

    if not args.object:
        raise Exception('No object specified')

    gitdir = lib.locate_dominating_file(pathlib.Path.cwd(), '.git')
    if not gitdir:
        raise Exception('Not a git repository')

    obj = git_object.from_sha(gitdir, args.type, args.object)

    if args.show_type:
        print(obj.type_.name.lower())
        return

    sys.stdout.buffer.write(obj.data)
