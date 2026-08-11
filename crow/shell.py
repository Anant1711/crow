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
