import json
import os
from datetime import date
from pathlib import Path


def _state_dir() -> Path:
    # $SNAP_USER_COMMON is the snap's own writable area, set automatically
    # by snapd for every app run — no interfaces/plugs needed, unlike the
    # real $HOME. Falls back to XDG state dir for non-snap installs.
    snap_common = os.environ.get("SNAP_USER_COMMON")
    if snap_common:
        return Path(snap_common)
    xdg_state = os.environ.get("XDG_STATE_HOME")
    base = Path(xdg_state) if xdg_state else Path.home() / ".local" / "state"
    return base / "crow"


def _state_path() -> Path:
    return _state_dir() / "state.json"


def read_index(day: date) -> int | None:
    """Return the overridden quote index for the given day, if any."""
    try:
        data = json.loads(_state_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if data.get("date") != day.isoformat():
        return None
    index = data.get("index")
    return index if isinstance(index, int) else None


def write_index(day: date, index: int) -> None:
    path = _state_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"date": day.isoformat(), "index": index}),
            encoding="utf-8",
        )
    except OSError:
        pass
