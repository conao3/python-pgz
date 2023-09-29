from __future__ import annotations

import argparse


def main(args: argparse.Namespace) -> None:
    print('init')
    return


def add_parser_init(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser('init')
    parser.set_defaults(handler=main)
