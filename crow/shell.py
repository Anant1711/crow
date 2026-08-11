BASH_INIT = """\
# crow shell integration for bash
__crow_precmd() {
  crow show
}

case ";${PROMPT_COMMAND};" in
  *";__crow_precmd;"*) ;;
  *) PROMPT_COMMAND="__crow_precmd${PROMPT_COMMAND:+;$PROMPT_COMMAND}" ;;
esac

trap '__crow_precmd' WINCH
trap 'crow reset' EXIT
"""

ZSH_INIT = """\
# crow shell integration for zsh
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
"""

SCRIPTS = {"bash": BASH_INIT, "zsh": ZSH_INIT}
