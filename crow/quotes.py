import json
from datetime import date
from importlib import resources


def load_quotes() -> list[str]:
    with resources.files("crow.data").joinpath("quotes.json").open(
        encoding="utf-8"
    ) as f:
        return json.load(f)


def today_quote(on: date | None = None) -> str:
    quotes = load_quotes()
    day = on or date.today()
    return quotes[day.toordinal() % len(quotes)]
