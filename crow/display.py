import shutil
import sys

CSI = "\033["

# DECSC/DECRC (ESC 7 / ESC 8) rather than the CSI "s"/"u" pair: the CSI form
# is xterm-era ANSI.SYS legacy with inconsistent support, while ESC 7/8 is
# core VT100/VT220 and reliably supported across terminal emulators. Cursor
# addressing after a margin change is absolute (CUP), so we never depend on
# where DECSTBM/DECRC happens to leave the cursor mid-sequence.
SAVE_CURSOR = "\0337"
RESTORE_CURSOR = "\0338"
CLEAR_LINE = f"{CSI}2K"
DIM = f"{CSI}2m"
RESET_STYLE = f"{CSI}0m"

# DEC private mode 2026: batches the terminal's repaint until the matching
# end marker, so a mid-sequence redraw is never shown half-applied. Ignored
# harmlessly by terminals that don't support it.
BEGIN_SYNC = f"{CSI}?2026h"
END_SYNC = f"{CSI}?2026l"


def _term_size() -> tuple[int, int]:
    size = shutil.get_terminal_size(fallback=(80, 24))
    return size.columns, size.lines


def _fit(text: str, width: int) -> str:
    if width <= 0:
        return ""
    if len(text) <= width:
        return text
    if width == 1:
        return "…"
    return text[: width - 1] + "…"


def show(quote: str) -> None:
    """Reserve the terminal's bottom row and draw the quote there."""
    if not sys.stdout.isatty():
        return
    cols, rows = _term_size()
    if rows < 3:
        return

    body_bottom = rows - 1
    text = _fit(quote, cols - 1)

    sequence = (
        BEGIN_SYNC
        + SAVE_CURSOR
        + f"{CSI}1;{body_bottom}r"  # reserve last row: scrolling region excludes it
        + f"{CSI}{rows};1H"  # absolute move to the reserved bottom row
        + CLEAR_LINE
        + DIM
        + text
        + RESET_STYLE
        + RESTORE_CURSOR  # back to wherever the shell had the cursor
        + END_SYNC
    )
    sys.stdout.write(sequence)
    sys.stdout.flush()


def reset() -> None:
    """Release the reserved bottom row and restore full-screen scrolling."""
    if not sys.stdout.isatty():
        return
    cols, rows = _term_size()

    sequence = (
        BEGIN_SYNC
        + SAVE_CURSOR
        + f"{CSI}r"  # full-screen scroll region
        + f"{CSI}{rows};1H"
        + CLEAR_LINE
        + RESTORE_CURSOR
        + END_SYNC
    )
    sys.stdout.write(sequence)
    sys.stdout.flush()
