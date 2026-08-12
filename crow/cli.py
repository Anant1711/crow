import argparse
import os
import sys

from . import display
from .quotes import today_quote
from .shell import SCRIPTS, detect_shell, install


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

    setup_p = sub.add_parser(
        "setup", help="add crow to your shell rc file automatically"
    )
    setup_p.add_argument(
        "shell",
        nargs="?",
        choices=sorted(SCRIPTS),
        default=None,
        help="defaults to your $SHELL",
    )

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
    elif args.command == "setup":
        shell = args.shell or detect_shell()
        if shell is None:
            print(
                "Couldn't detect your shell from $SHELL. Run `crow setup bash` "
                "or `crow setup zsh` to pick one explicitly.",
                file=sys.stderr,
            )
            return 1
        status, rc_path = install(shell)
        if status == "added":
            print(f"Added crow to {rc_path}. Open a new terminal to see it in action.")
        elif status == "already":
            print(f"crow is already set up in {rc_path}.")
        else:
            eval_line = f'eval "$(crow init {shell})"'
            print(
                f"Couldn't write to {rc_path} automatically.\n"
                f"Add this line to it yourself:\n  {eval_line}",
                file=sys.stderr,
            )
            return 1
    elif args.command == "show":
        display.show(today_quote())
    elif args.command == "reset":
        display.reset()
    else:
        print(today_quote())
        if not os.environ.get("CROW_ACTIVE"):
            print(
                "\ntip: crow isn't wired into your shell yet — run `crow setup`",
                file=sys.stderr,
            )

    return 0
