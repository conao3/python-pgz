from __future__ import annotations

import pathlib
import sys

import pydantic

from .. import lib
from .. import types
from .. import git_object


class Argument(pydantic.BaseModel):
    type: types.GitObjectTypeEnum
    object: str

    @classmethod
    def parse_args(cls, args_: list[str]) -> Argument:
        args: list[str] = []

        while args_:
            arg = args_.pop(0)
            if arg == '--':
                args.extend(args_)
                break
            elif arg.startswith('-'):
                raise Exception(f'Unknown option: {arg}')
            else:
                args.append(arg)

        type_, obj = args

        enum_type = types.GitObjectTypeEnum.from_str(type_)
        if not enum_type:
            raise Exception(f'Unknown type: {type_}')

        return cls(
            type=enum_type,
            object=obj,
        )


def main_cat_file(args_: list[str]) -> None:
    args = Argument.parse_args(args_)

    gitdir = lib.locate_dominating_file(pathlib.Path.cwd(), '.git')
    if not gitdir:
        raise Exception('Not a git repository')

    obj = git_object.from_sha(gitdir, args.type, args.object)
    sys.stdout.buffer.write(obj.data)
