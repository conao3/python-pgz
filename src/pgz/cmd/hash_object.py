from __future__ import annotations

import pathlib
from typing import Optional

import pydantic

from .. import lib
from .. import types
from .. import git_object


class Argument(pydantic.BaseModel):
    type: types.GitObjectTypeEnum = types.GitObjectTypeEnum.BLOB
    write: bool = False
    filepath: Optional[pathlib.Path] = None

    @classmethod
    def parse_args(cls, args_: list[str]) -> Argument:
        def help() -> None:
            print('''\
hash-object: Compute object ID and optionally creates a blob from a file.

Usage: pgz hash-object [options...] <file>

Arguments:
    <file>    Specify the file.

Options:
    -h, --help    Show this message and exit.
    -w            Actually write the object into the object database.
    -t <type>     Specify the type.  (commit, tree, tag, blob) (default: blob)
''')

        obj = cls()
        args: list[str] = []

        while args_:
            arg = args_.pop(0)
            if arg == '-w':
                obj.write = True
            elif arg == '-t':
                raw_type = args_.pop(0)
                type_ = types.GitObjectTypeEnum.from_str(raw_type)
                if not type_:
                    raise Exception(f'Unknown type: {type_}')
                obj.type = type_
            elif arg in ('-h', '--help'):
                help()
                exit(0)
            elif arg == '--':
                args.extend(args_)
                break
            elif arg.startswith('-'):
                raise Exception(f'Unknown option: {arg}')
            else:
                args.append(arg)

        filepath_, = args

        obj.filepath = pathlib.Path(filepath_)

        return obj


def main_hash_object(args_: list[str]) -> None:
    args = Argument.parse_args(args_)

    obj = git_object.from_path(args.type, args.filepath)

    if args.write:
        gitdir = lib.locate_dominating_file(pathlib.Path.cwd(), '.git')
        if not gitdir:
            raise Exception('Not a git repository')

        git_object.write_obj(obj, gitdir)

    print(git_object.obj_hash(obj))
