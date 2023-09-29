from __future__ import annotations

import pathlib
from typing import Optional

import pydantic

from .. import lib


class Argument(pydantic.BaseModel):
    ref: Optional[str] = None
    newvalue: Optional[str] = None

    @classmethod
    def parse_args(cls, args_: list[str]) -> Argument:
        def help() -> None:
            print('''\
update-ref: Update the object name stored in a ref safely.

Usage: pgz update-ref [options...] <ref> <newvalue>

Arguments:
    <ref>       Specify the ref.
    <newvalue>  Specify the new value.

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

        if len(args) == 2:
            obj.ref, obj.newvalue = args
        else:
            raise Exception('Invalid arguments')

        return obj


def main_update_ref(args_: list[str]) -> None:
    args = Argument.parse_args(args_)

    if not args.ref or not args.newvalue:
        raise Exception('Invalid arguments')

    gitdir = lib.locate_dominating_file(pathlib.Path.cwd(), '.git')
    if not gitdir:
        raise Exception('Not a git repository')

    with lib.create_repo_file(gitdir, args.ref).open('w') as f:
        f.write(args.newvalue + '\n')
