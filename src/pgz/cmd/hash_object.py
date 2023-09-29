from __future__ import annotations

import argparse
import pathlib

from .. import lib
from .. import types
from .. import git_object


def main(args: argparse.Namespace) -> None:
    filepath = pathlib.Path(args.file)
    type_ = types.GitObjectTypeEnum.from_str(args.type)
    if not type_:
        raise Exception(f'Unknown type: {args.type}')

    obj = git_object.from_path(type_, filepath)

    if args.write:
        gitdir = lib.locate_dominating_file(pathlib.Path.cwd(), '.git')
        if not gitdir:
            raise Exception('Not a git repository')

        git_object.write_obj(obj, gitdir)

    print(git_object.obj_hash(obj))

    return


def add_parser_hash_object(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore
    parser = subparsers.add_parser('hash-object')
    parser.add_argument('-t', '--type', choices=['blob', 'commit', 'tag', 'tree'], default='blob')
    parser.add_argument('-w', '--write', action='store_true')
    parser.add_argument('file')

    parser.set_defaults(handler=main)
