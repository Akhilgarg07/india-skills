#!/usr/bin/env python3
"""Indian financial year (April-March), assessment year vs tax year, quarters, IST
conversion and strict DD/MM/YYYY parsing.

  * Financial year (FY) runs 1 April - 31 March (General Clauses Act, 1897). Label "2026-27".
  * Income-tax Act 1961 (income up to FY 2025-26): income of FY X-(X+1) is assessed in
    assessment year (AY) (X+1)-(X+2). E.g. FY 2025-26 -> AY 2026-27.
  * Income-tax Act 2025 (from 1 April 2026): "tax year" = the FY itself. FY 2026-27 is
    "Tax Year 2026-27"; there is no separate assessment year.
  * IST = UTC+05:30, no daylight saving (IANA zone Asia/Kolkata; Asia/Calcutta is an alias).

Module usage:
    >>> import datetime as dt
    >>> from fiscal_year import financial_year, parse_ddmmyyyy, to_ist
    >>> fy = financial_year(dt.date(2026, 3, 31))
    >>> fy["label"], fy["assessment_year"], fy["quarter"]
    ('2025-26', '2026-27', 'Q4')
    >>> financial_year(dt.date(2026, 4, 1))["tax_year"]
    'Tax Year 2026-27'
    >>> parse_ddmmyyyy("01/04/2026")
    datetime.date(2026, 4, 1)
    >>> to_ist(dt.datetime(2026, 3, 31, 20, 15, tzinfo=dt.timezone.utc)).isoformat()
    '2026-04-01T01:45:00+05:30'

CLI usage:
    python3 fiscal_year.py fy 2026-03-31          # FY, AY / tax year, quarter, start/end
    python3 fiscal_year.py fy 31/03/2026
    python3 fiscal_year.py ist 2026-03-31T20:15:00Z

Standard library only.
"""

import datetime as dt
import json
import re
import sys

IST = dt.timezone(dt.timedelta(hours=5, minutes=30), "IST")
NEW_ACT_FROM = dt.date(2026, 4, 1)
_DDMMYYYY = re.compile(r"^(\d{2})([/.-])(\d{2})\2(\d{4})$")


def fy_start_year(d: dt.date) -> int:
    return d.year if d.month >= 4 else d.year - 1


def fy_label(start_year: int) -> str:
    """2026 -> '2026-27'."""
    return f"{start_year}-{(start_year + 1) % 100:02d}"


def financial_year(d) -> dict:
    """Everything about the Indian FY containing date d (date, datetime, or 'YYYY-MM-DD' / 'DD/MM/YYYY')."""
    if isinstance(d, dt.datetime):
        d = to_ist(d).date() if d.tzinfo else d.date()
    elif isinstance(d, str):
        d = parse_date(d)
    start = fy_start_year(d)
    month_index = (d.month - 4) % 12 + 1          # April = 1 ... March = 12
    quarter = (month_index - 1) // 3 + 1
    first_day = dt.date(start, 4, 1)
    under_new_act = first_day >= NEW_ACT_FROM
    return {
        "date": d.isoformat(),
        "label": fy_label(start),
        "start": first_day.isoformat(),
        "end": dt.date(start + 1, 3, 31).isoformat(),
        "quarter": f"Q{quarter}",
        "month_of_fy": month_index,
        "income_tax_act": "Income-tax Act 2025" if under_new_act else "Income-tax Act 1961",
        "tax_year": f"Tax Year {fy_label(start)}" if under_new_act else None,
        "assessment_year": None if under_new_act else fy_label(start + 1),
    }


def quarter_range(start_year: int, quarter: int):
    """(first_day, last_day) of FY quarter 1-4 for the FY starting in start_year."""
    if quarter not in (1, 2, 3, 4):
        raise ValueError("quarter must be 1-4")
    m = 4 + 3 * (quarter - 1)
    y = start_year if m <= 12 else start_year + 1
    m = m if m <= 12 else m - 12
    first = dt.date(y, m, 1)
    nm, ny = (m + 3, y) if m + 3 <= 12 else (m + 3 - 12, y + 1)
    return first, dt.date(ny, nm, 1) - dt.timedelta(days=1)


def parse_ddmmyyyy(text: str) -> dt.date:
    """Strict DD/MM/YYYY (also DD-MM-YYYY, DD.MM.YYYY). Never guesses MM/DD."""
    m = _DDMMYYYY.match(str(text).strip())
    if not m:
        raise ValueError(f"{text!r} is not DD/MM/YYYY (two-digit day and month, four-digit year)")
    day, _, month, year = m.groups()
    try:
        return dt.date(int(year), int(month), int(day))
    except ValueError as exc:
        raise ValueError(f"{text!r}: {exc}") from None


def parse_date(text: str) -> dt.date:
    """ISO YYYY-MM-DD or strict DD/MM/YYYY."""
    t = str(text).strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", t):
        return dt.date.fromisoformat(t)
    return parse_ddmmyyyy(t)


def format_ddmmyyyy(d: dt.date, sep: str = "/") -> str:
    return f"{d.day:02d}{sep}{d.month:02d}{sep}{d.year:04d}"


def to_ist(moment: dt.datetime) -> dt.datetime:
    """Convert an aware datetime to IST. Naive datetimes are rejected (ambiguous)."""
    if moment.tzinfo is None:
        raise ValueError("naive datetime: attach a timezone (e.g. UTC) before converting")
    return moment.astimezone(IST)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    try:
        if len(argv) == 2 and argv[0] == "fy":
            print(json.dumps(financial_year(argv[1]), indent=2))
            return 0
        if len(argv) == 2 and argv[0] == "ist":
            s = argv[1].replace("Z", "+00:00")
            print(to_ist(dt.datetime.fromisoformat(s)).isoformat())
            return 0
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print("usage: fiscal_year.py fy DATE | fiscal_year.py ist ISO_DATETIME_WITH_OFFSET", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
