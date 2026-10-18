#!/usr/bin/env python3
"""Amount in words in Indian English, using the Indian numbering system
(thousand, lakh, crore; larger amounts as "... lakh crore", "... thousand crore").

    120000      -> "One Lakh Twenty Thousand Rupees Only"
    1050.50     -> "One Thousand Fifty Rupees and Fifty Paise Only"
    prefix style -> "Rupees One Lakh Twenty Thousand Only"

Module usage:
    >>> from amount_in_words import amount_in_words, number_to_words
    >>> amount_in_words(120000)
    'One Lakh Twenty Thousand Rupees Only'
    >>> amount_in_words("1050.50", style="prefix")
    'Rupees One Thousand Fifty and Fifty Paise Only'
    >>> number_to_words(10_00_00_00_00_000)
    'One Lakh Crore'

CLI usage:
    python3 amount_in_words.py 120000
    python3 amount_in_words.py 1050.50 --prefix
    python3 amount_in_words.py 105 --and          # One Hundred and Five Rupees Only

Standard library only.
"""

import argparse
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

ONES = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
        "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen",
        "Nineteen"]
TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def _below_100(n):
    if n < 20:
        return ONES[n]
    t, o = divmod(n, 10)
    return TENS[t] + (" " + ONES[o] if o else "")


def _below_1000(n, use_and):
    h, r = divmod(n, 100)
    parts = []
    if h:
        parts.append(ONES[h] + " Hundred")
    if r:
        if h and use_and:
            parts.append("and")
        parts.append(_below_100(r))
    return " ".join(parts)


def number_to_words(n: int, use_and: bool = False) -> str:
    """Non-negative integer to Indian-English words (Title Case)."""
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        raise ValueError("number_to_words expects a non-negative int")
    if n == 0:
        return "Zero"
    crore, rest = divmod(n, 10_000_000)
    lakh, rest = divmod(rest, 100_000)
    thousand, rest = divmod(rest, 1000)
    parts = []
    if crore:
        parts.append(number_to_words(crore, use_and) + " Crore")
    if lakh:
        parts.append(_below_100(lakh) + " Lakh")
    if thousand:
        parts.append(_below_100(thousand) + " Thousand")
    if rest:
        if parts and use_and and rest < 100:
            parts.append("and")
        parts.append(_below_1000(rest, use_and))
    return " ".join(parts)


def amount_in_words(amount, style: str = "suffix", use_and: bool = False, only: bool = True) -> str:
    """Rupees and paise in words. style='suffix' -> '... Rupees Only'; 'prefix' -> 'Rupees ... Only'.

    Amounts are rounded half-up to paise. Pass str/Decimal/int, not float, for money.
    """
    if isinstance(amount, float):
        amount = repr(amount)
    try:
        d = Decimal(str(amount).replace(",", "").replace("₹", "").strip())
    except InvalidOperation:
        raise ValueError(f"{amount!r} is not a number") from None
    if not d.is_finite():
        raise ValueError("amount must be finite")
    if style not in ("suffix", "prefix"):
        raise ValueError("style must be 'suffix' or 'prefix'")
    neg = d < 0
    d = abs(d).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    rupees = int(d)
    paise = int((d - rupees) * 100)

    r_words = number_to_words(rupees, use_and)
    p_words = number_to_words(paise, use_and) if paise else None
    tail = " Only" if only else ""
    if style == "suffix":
        unit = "Rupee" if rupees == 1 else "Rupees"
        if rupees == 0 and p_words:
            text = f"{p_words} {'Paisa' if paise == 1 else 'Paise'}"
        else:
            text = f"{r_words} {unit}"
            if p_words:
                text += f" and {p_words} {'Paisa' if paise == 1 else 'Paise'}"
    else:
        if rupees == 0 and p_words:
            text = f"{'Paisa' if paise == 1 else 'Paise'} {p_words}"
        else:
            text = f"Rupees {r_words}"
            if p_words:
                text += f" and {p_words} {'Paisa' if paise == 1 else 'Paise'}"
    return ("Minus " if neg else "") + text + tail


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Amount in words (Indian English)")
    p.add_argument("amount")
    p.add_argument("--prefix", action="store_true", help="'Rupees ... Only' style")
    p.add_argument("--and", dest="use_and", action="store_true", help="'One Hundred and Five'")
    p.add_argument("--no-only", action="store_true")
    a = p.parse_args(argv)
    try:
        print(amount_in_words(a.amount, "prefix" if a.prefix else "suffix", a.use_and, not a.no_only))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
