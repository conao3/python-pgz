import argparse
import inspect

from . import cmd

def list_main_functions() -> list[str]:
    fns = inspect.getmembers(cmd, inspect.isfunction)
    return list(elm[0] for elm in fns if elm[0].startswith('main_'))


def parse_args() -> tuple[argparse.ArgumentParser, argparse.Namespace]:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    fns = inspect.getmembers(cmd, inspect.isfunction)
    for add_parser in [elm[1] for elm in fns if elm[0].startswith('add_parser_')]:
        add_parser(subparsers)

    return parser, parser.parse_args()


def main() -> None:
    parser, args = parse_args()

    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        parser.print_help()
