# crow

A daily quote, pinned to the bottom line of your terminal.

crow reserves the last line of your terminal and keeps a short,
programmer-flavored quote there — through commands, output, and window
resizes — without touching your scrollback. The quote changes once a day.

```
$ ls
Cargo.toml  src/  target/
────────────────────────────────────────────────────────────
git blame is just archaeology with extra steps.
```

## Install

```
snap install crow
```

## Usage

Add one line to your shell rc file:

```bash
# ~/.bashrc
eval "$(crow init bash)"
```

```zsh
# ~/.zshrc
eval "$(crow init zsh)"
```

Open a new terminal and the quote appears on the bottom line, refreshing
after every command and on resize. It's cleared automatically when the
shell exits.

If you just want today's quote printed once, with no terminal trickery:

```
$ crow today
```

## How it works

`crow show` uses ANSI escape codes to shrink the terminal's scrolling
region by one row and draw the quote in the row left over, then restores
the cursor to wherever the shell had it. The shell integration script
calls `crow show` before every prompt (so the line survives whatever the
last command printed) and on `SIGWINCH` (so it survives resizes), then
calls `crow reset` on shell exit to give the terminal back its full
scrolling region.

Quotes are bundled with the snap as a static list and picked
deterministically by the current date, so crow works fully offline and
never phones home.

## License

MIT
