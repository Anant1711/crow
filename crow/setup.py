import os
import pwd
import sys
from pathlib import Path

from .shell import SCRIPTS

MARKER = "crow init"


def _detect_shell() -> str | None:
    name = os.environ.get("SHELL", "").rsplit("/", 1)[-1]
    return name if name in SCRIPTS else None


def _real_home() -> Path:
    # Under strict snap confinement, $HOME (and Path.home()) is remapped to
    # the snap's private per-revision data dir, not the user's actual home.
    # The passwd database isn't subject to that remapping, so it's the only
    # reliable way to find where ~/.bashrc actually lives.
    try:
        return Path(pwd.getpwuid(os.getuid()).pw_dir)
    except (KeyError, OSError):
        return Path.home()


def _rc_path(shell: str) -> Path:
    return _real_home() / (".zshrc" if shell == "zsh" else ".bashrc")


def ensure_shell_integration() -> str | None:
    """On first interactive run, wire crow into the user's shell rc file.

    Returns a one-line status message to print, or None to stay silent
    (already set up, non-interactive, or shell unrecognized).
    """
    if not sys.stdout.isatty():
        return None

    shell = _detect_shell()
    if shell is None:
        return None

    rc = _rc_path(shell)
    eval_line = f'eval "$(crow init {shell})"'
    fallback = f"crow needs one-time setup: add this line to {rc}:\n  {eval_line}"

    try:
        existing = rc.read_text(encoding="utf-8") if rc.exists() else ""
    except OSError:
        return fallback

    if MARKER in existing:
        return None

    block = f"\n# crow: pin a daily quote to your terminal's bottom line\n{eval_line}\n"

    try:
        with rc.open("a", encoding="utf-8") as f:
            f.write(block)
    except OSError:
        return fallback

    return f"Added crow to {rc} — open a new terminal to see it in action."
