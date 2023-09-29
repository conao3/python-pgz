import inspect
import sys

from . import cmd


def list_main_functions() -> list[str]:
    fns = inspect.getmembers(cmd, inspect.isfunction)
    return list(elm[0] for elm in fns if elm[0].startswith('main_'))


def main() -> None:
    _executable, command_, *args = sys.argv
    command = 'main_' + command_.replace('-', '_')

    commands = list_main_functions()
    if command not in commands:
        raise Exception(f'Unknown command: {command_}.  Available commands: {[elm[5:].replace("_", "-") for elm in commands]}')

    getattr(cmd, command)(args)
