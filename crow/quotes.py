import json
import random
from datetime import date
from importlib import resources

from . import state


def load_quotes() -> list[str]:
    with resources.files("crow.data").joinpath("quotes.json").open(
        encoding="utf-8"
    ) as f:
        return json.load(f)


def _daily_index(quotes: list[str], day: date) -> int:
    return day.toordinal() % len(quotes)


def _effective_index(quotes: list[str], day: date) -> int:
    index = state.read_index(day)
    if index is None or not (0 <= index < len(quotes)):
        return _daily_index(quotes, day)
    return index


def today_quote(on: date | None = None) -> str:
    quotes = load_quotes()
    day = on or date.today()
    return quotes[_effective_index(quotes, day)]


def shuffle_quote() -> str:
    """Pick a different quote for today and remember it for the rest of the day."""
    quotes = load_quotes()
    today = date.today()
    current = _effective_index(quotes, today)
    choices = [i for i in range(len(quotes)) if i != current] or [current]
    index = random.choice(choices)
    state.write_index(today, index)
    return quotes[index]
