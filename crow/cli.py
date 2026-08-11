import argparse
import sys

from . import display
from .quotes import today_quote
from .shell import SCRIPTS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crow",
        description="A daily quote, pinned to the bottom line of your terminal.",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("today", help="print today's quote and exit")

    init_p = sub.add_parser(
        "init", help="print shell integration script (eval it in your rc file)"
    )
    init_p.add_argument("shell", choices=sorted(SCRIPTS))

    # Internal commands invoked by the shell integration script; not meant
    # to be run by hand, so they're left out of --help.
    sub.add_parser("show", help=argparse.SUPPRESS)
    sub.add_parser("reset", help=argparse.SUPPRESS)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        sys.stdout.write(SCRIPTS[args.shell])
    elif args.command == "show":
        display.show(today_quote())
    elif args.command == "reset":
        display.reset()
    else:
        print(today_quote())

    return 0
