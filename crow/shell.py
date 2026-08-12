import os
import pwd
from pathlib import Path

BASH_INIT = """\
# crow shell integration for bash
export CROW_ACTIVE=1
__crow_precmd() {
  crow show
}

case ";${PROMPT_COMMAND};" in
  *";__crow_precmd;"*) ;;
  *) PROMPT_COMMAND="__crow_precmd${PROMPT_COMMAND:+;$PROMPT_COMMAND}" ;;
esac

trap '__crow_precmd' WINCH
trap 'crow reset' EXIT

crow_off() {
  PROMPT_COMMAND="${PROMPT_COMMAND//__crow_precmd;/}"
  PROMPT_COMMAND="${PROMPT_COMMAND//__crow_precmd/}"
  trap - WINCH
  trap - EXIT
  crow reset
}
"""

ZSH_INIT = """\
# crow shell integration for zsh
export CROW_ACTIVE=1
autoload -Uz add-zsh-hook

__crow_precmd() {
  crow show
}

__crow_on_exit() {
  crow reset
}

add-zsh-hook precmd __crow_precmd
add-zsh-hook zshexit __crow_on_exit

TRAPWINCH() {
  crow show
}

crow_off() {
  add-zsh-hook -d precmd __crow_precmd
  add-zsh-hook -d zshexit __crow_on_exit
  unfunction TRAPWINCH 2>/dev/null
  crow reset
}
"""

SCRIPTS = {"bash": BASH_INIT, "zsh": ZSH_INIT}

RC_FILES = {"bash": ".bashrc", "zsh": ".zshrc"}

MARKER = "crow init"


def detect_shell() -> str | None:
    """Guess the user's shell from $SHELL. Returns None if unsupported."""
    name = Path(os.environ.get("SHELL", "")).name
    return name if name in SCRIPTS else None


def _real_home() -> Path:
    # Under strict snap confinement, $HOME (and Path.home()/expanduser()) is
    # remapped to the snap's private per-revision data dir, not the user's
    # actual home. The passwd database isn't subject to that remapping, so
    # it's the only reliable way to find where the rc file actually lives.
    try:
        return Path(pwd.getpwuid(os.getuid()).pw_dir)
    except (KeyError, OSError):
        return Path.home()


def install(shell: str) -> tuple[str, Path]:
    """Append the crow eval line to the shell's rc file if not already there.

    Returns (status, rc_path). status is one of:
      "added"   - the line was just appended
      "already" - it was already there
      "blocked" - couldn't read or write the file (e.g. a strictly confined
                  snap install with no permission to touch files outside
                  its own sandbox); rc_path is still the real path, so the
                  caller can tell the user what to add by hand.
    """
    rc_path = _real_home() / RC_FILES[shell]

    try:
        existing = rc_path.read_text(encoding="utf-8") if rc_path.exists() else ""
    except OSError:
        return "blocked", rc_path

    if MARKER in existing:
        return "already", rc_path

    block = f'\n# Added by `crow setup`\neval "$(crow init {shell})"\n'
    try:
        rc_path.parent.mkdir(parents=True, exist_ok=True)
        with rc_path.open("a", encoding="utf-8") as f:
            if existing and not existing.endswith("\n"):
                f.write("\n")
            f.write(block)
    except OSError:
        return "blocked", rc_path

    return "added", rc_path
