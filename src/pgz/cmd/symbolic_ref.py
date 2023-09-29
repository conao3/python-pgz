from __future__ import annotations

import pathlib
from typing import Optional

import pydantic

from .. import lib


class Argument(pydantic.BaseModel):
    name: Optional[str] = None
    ref: Optional[str] = None

    @classmethod
    def parse_args(cls, args_: list[str]) -> Argument:
        def help() -> None:
            print('''\
symbolic-ref: Update the object name stored in a ref safely.

Usage: pgz symbolic-ref [options...] <name> <ref>

Arguments:
    <name>  Specify the name.
    <ref>   Specify the ref.

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
            obj.name = args[0]
        elif len(args) == 2:
            obj.name, obj.ref = args
        else:
            raise Exception('Invalid arguments')

        return obj


def main_symbolic_ref(args_: list[str]) -> None:
    args = Argument.parse_args(args_)

    if not args.name:
        raise Exception('Invalid arguments')

    gitdir = lib.locate_dominating_file(pathlib.Path.cwd(), '.git')
    if not gitdir:
        raise Exception('Not a git repository')

    if args.ref:
        with lib.get_or_create_repo_file(gitdir, args.name).open('w') as f:
            f.write(f'ref: {args.ref}\n')
        return

    print(lib.get_or_create_repo_file(gitdir, args.name).read_text().strip()[5:])
