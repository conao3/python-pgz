from __future__ import annotations

import argparse
import pathlib
import sys

from .. import lib
from .. import types
from .. import git_object

def main(args: argparse.Namespace) -> None:
    gitdir = lib.locate_dominating_file(pathlib.Path.cwd(), '.git')
    if not gitdir:
        raise Exception('Not a git repository')

    type_ = types.GitObjectTypeEnum.from_str(args.type)
    if not type_:
        raise Exception(f'Unknown type: {args.type}')

    obj = git_object.from_sha(gitdir, type_, args.object)
    sys.stdout.buffer.write(obj.data)
    return


def add_parser_cat_file(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore
    parser = subparsers.add_parser('cat-file')
    parser.add_argument('type', choices=['blob', 'commit', 'tag', 'tree'])
    parser.add_argument('object')

    parser.set_defaults(handler=main)
