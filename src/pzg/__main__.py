import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('command')

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(args)
