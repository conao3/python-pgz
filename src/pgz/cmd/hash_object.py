from __future__ import annotations

import pathlib

import pydantic

from .. import lib
from .. import types
from .. import git_object


class Argument(pydantic.BaseModel):
    type: types.GitObjectTypeEnum
    write: bool
    filepath: pathlib.Path

    @classmethod
    def parse_args(cls, args_: list[str]) -> Argument:
        args: list[str] = []
        type_ = types.GitObjectTypeEnum.BLOB
        write_ = False
        file_ = None

        while args_:
            arg = args_.pop(0)
            if arg == '-w':
                write_ = True
            elif arg == '-t':
                raw_type = args_.pop(0)
                type_ = types.GitObjectTypeEnum.from_str(raw_type)
                if not type_:
                    raise Exception(f'Unknown type: {type_}')
            elif arg == '--':
                args.extend(args_)
                break
            elif arg.startswith('-'):
                raise Exception(f'Unknown option: {arg}')
            else:
                args.append(arg)

        file_, = args

        return cls(
            type=type_,
            write=write_,
            filepath=pathlib.Path(file_),
        )


def main_hash_object(args_: list[str]) -> None:
    args = Argument.parse_args(args_)

    obj = git_object.from_path(args.type, args.filepath)

    if args.write:
        gitdir = lib.locate_dominating_file(pathlib.Path.cwd(), '.git')
        if not gitdir:
            raise Exception('Not a git repository')

        git_object.write_obj(obj, gitdir)

    print(git_object.obj_hash(obj))
