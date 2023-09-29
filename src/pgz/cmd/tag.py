from __future__ import annotations

import pathlib
from typing import Optional

import pydantic

from .. import lib
from .. import types
from .. import git_object


class Argument(pydantic.BaseModel):
    tagname: Optional[str] = None
    obj: Optional[str] = None

    annotate: bool = False
    message: Optional[str] = None

    @classmethod
    def parse_args(cls, args_: list[str]) -> Argument:
        def help() -> None:
            print('''\
tag: Create, list, delete tag object

Usage: pgz tag [options...] <tagname> [<object>]

Arguments:
    <tagname>  Specify the tag name.
    <object>   Specify the object.

Options:
    -a, --annotate  Create an annotated tag object.
    -m <message>    Specify the tag message.
    -h, --help      Show this message and exit.
''')

        obj = cls()
        args: list[str] = []

        while args_:
            arg = args_.pop(0)
            if arg in ('-a', '--annotate'):
                obj.annotate = True
            if arg == '-m':
                obj.message = args_.pop(0)
                obj.annotate = True
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

        obj.tagname, obj.obj, *_ = args + [None, None]

        return obj


def main_tag(args_: list[str]) -> None:
    args = Argument.parse_args(args_)

    gitdir = lib.locate_dominating_file(pathlib.Path.cwd(), '.git')
    if not gitdir:
        raise Exception('Not a git repository')

    if not args.tagname:
        raise Exception('Invalid arguments')

    if not args.obj:
        raise Exception('Invalid arguments')

    if args.annotate:
        if not args.message:
            raise Exception('Invalid arguments')

        obj = types.GitObjectTag(
            type_=types.GitObjectTypeEnum.TAG,
            object=args.obj,
            type='commit',
            tag=args.tagname,
            tagger=b'',
            message=args.message.encode(),
        )

        sha, _ = git_object.write_(obj, gitdir)

        filepath = lib.get_or_create_repo_file(gitdir, f'refs/tags/{args.tagname}')
        filepath.write_text(f'{sha}\n')
        return

    filepath = lib.get_or_create_repo_file(gitdir, f'refs/tags/{args.tagname}')
    filepath.write_text(f'{args.obj}\n')
