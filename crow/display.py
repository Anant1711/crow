import shutil
import sys

CSI = "\033["

SAVE_CURSOR = f"{CSI}s"
RESTORE_CURSOR = f"{CSI}u"
CLEAR_LINE = f"{CSI}2K"
DIM = f"{CSI}2m"
RESET_STYLE = f"{CSI}0m"


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
        SAVE_CURSOR
        + f"{CSI}1;{body_bottom}r"  # reserve last row: scrolling region excludes it
        + RESTORE_CURSOR  # margin change resets cursor to 1,1; put it back first
        + f"{CSI}{rows};1H"  # then move to the reserved bottom row
        + CLEAR_LINE
        + DIM
        + text
        + RESET_STYLE
        + RESTORE_CURSOR  # and put the cursor back where the shell expects it
    )
    sys.stdout.write(sequence)
    sys.stdout.flush()


def reset() -> None:
    """Release the reserved bottom row and restore full-screen scrolling."""
    if not sys.stdout.isatty():
        return
    cols, rows = _term_size()

    sequence = (
        SAVE_CURSOR
        + f"{CSI}r"  # full-screen scroll region
        + RESTORE_CURSOR
        + f"{CSI}{rows};1H"
        + CLEAR_LINE
        + RESTORE_CURSOR
    )
    sys.stdout.write(sequence)
    sys.stdout.flush()
