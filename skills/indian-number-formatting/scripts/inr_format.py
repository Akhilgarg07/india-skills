#!/usr/bin/env python3
"""Indian digit grouping (lakh/crore), ₹ formatting, parsing, and lakh/crore short forms.

Grouping follows Unicode CLDR for en-IN (pattern "#,##,##0.###"): the last three integer
digits form one group, then groups of two: 1,00,000 (one lakh), 1,00,00,000 (one crore),
12,34,56,789. This is exactly what Intl.NumberFormat("en-IN") produces.

Module usage:
    >>> from inr_format import group_indian, format_inr, parse_indian, short_lakh_crore
    >>> group_indian(123456789)
    '12,34,56,789'
    >>> format_inr("1234567.5")
    '₹12,34,567.50'
    >>> format_inr(-1500, decimals=0)
    '-₹1,500'
    >>> parse_indian("₹12,34,567.50")
    Decimal('1234567.50')
    >>> short_lakh_crore(1250000)
    '12.5 lakh'

CLI usage:
    python3 inr_format.py 1234567.5            # ₹12,34,567.50
    python3 inr_format.py 120000 --decimals 0  # ₹1,20,000
    python3 inr_format.py 25000000 --short     # 2.5 crore

Standard library only.
"""

import argparse
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

RUPEE = "₹"  # ₹ INDIAN RUPEE SIGN
LAKH = Decimal(100_000)
CRORE = Decimal(10_000_000)


def _d(value) -> Decimal:
    if isinstance(value, float):
        value = repr(value)
    try:
        d = Decimal(str(value).strip())
    except InvalidOperation:
        raise ValueError(f"{value!r} is not a number") from None
    if not d.is_finite():
        raise ValueError("number must be finite")
    return d


def group_indian(integer_digits) -> str:
    """Group a non-negative integer (int or digit string) the Indian way."""
    s = str(integer_digits)
    if not s.isdigit():
        raise ValueError("group_indian expects a non-negative integer")
    s = s.lstrip("0") or "0"
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return ",".join(groups + [tail])


def format_indian(value, decimals=None) -> str:
    """12,34,567.891 style. decimals=None keeps the value's own digits."""
    d = _d(value)
    if decimals is not None:
        d = d.quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)
    sign = "-" if d < 0 else ""
    text = format(abs(d), "f")
    int_part, _, frac = text.partition(".")
    out = group_indian(int_part)
    return f"{sign}{out}.{frac}" if frac else f"{sign}{out}"


def format_inr(value, decimals=2, symbol=True, space=False) -> str:
    """₹12,34,567.50. Minus sign before the symbol, as Intl.NumberFormat('en-IN') does."""
    d = _d(value)
    body = format_indian(abs(d), decimals)
    prefix = (RUPEE + (" " if space else "")) if symbol else ""
    if d < 0 and Decimal(body.replace(",", "")) != 0:
        return f"-{prefix}{body}"
    return f"{prefix}{body}"


def parse_indian(text) -> Decimal:
    """Parse '₹ 12,34,567.50', 'Rs. 1,20,000', '1,20,000/-' or '-₹500' into a Decimal.

    Accepts commas in any position (user input is inconsistent) but nothing else odd.
    """
    t = str(text).strip()
    neg = t.startswith("-")
    t = t.lstrip("-").strip()
    for p in (RUPEE, "Rs.", "Rs", "INR", "rs.", "rs"):
        if t.startswith(p):
            t = t[len(p):].strip()
            break
    if t.endswith("/-"):
        t = t[:-2].strip()
    if t.startswith("-"):
        neg, t = True, t[1:].strip()
    t = t.replace(",", "")
    if not t or not all(c.isdigit() or c == "." for c in t) or t.count(".") > 1:
        raise ValueError(f"cannot parse {text!r} as an Indian-formatted number")
    d = Decimal(t)
    return -d if neg else d


def short_lakh_crore(value, digits=2, long_words=True) -> str:
    """1250000 -> '12.5 lakh', 25000000 -> '2.5 crore'. Explicit rounding, trailing zeros trimmed."""
    d = _d(value)
    sign = "-" if d < 0 else ""
    a = abs(d)
    if a >= CRORE:
        n, unit = a / CRORE, ("crore" if long_words else "Cr")
    elif a >= LAKH:
        n, unit = a / LAKH, ("lakh" if long_words else "L")
    else:
        return sign + format_indian(a.quantize(Decimal(1), ROUND_HALF_UP))
    q = n.quantize(Decimal(1).scaleb(-digits), ROUND_HALF_UP)
    if unit in ("lakh", "L") and q >= 100:  # 99,99,999 rounds to 100 lakh -> say 1 crore
        q, unit = (q / 100).quantize(Decimal(1).scaleb(-digits), ROUND_HALF_UP), ("crore" if long_words else "Cr")
    q = q.normalize()
    num = format_indian(format(q, "f"))
    return f"{sign}{num} {unit}" if long_words else f"{sign}{num}{unit}"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Indian number / INR formatting")
    p.add_argument("value")
    p.add_argument("--decimals", type=int, default=2)
    p.add_argument("--no-symbol", action="store_true")
    p.add_argument("--short", action="store_true", help="lakh/crore short form")
    p.add_argument("--parse", action="store_true", help="parse an Indian-formatted string")
    a = p.parse_args(argv)
    try:
        if a.parse:
            print(parse_indian(a.value))
        elif a.short:
            print(short_lakh_crore(a.value))
        else:
            print(format_inr(a.value, a.decimals, symbol=not a.no_symbol))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
