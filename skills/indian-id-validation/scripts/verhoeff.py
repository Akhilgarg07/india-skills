#!/usr/bin/env python3
"""Verhoeff checksum (dihedral group D5), as required by UIDAI for Aadhaar numbers.

UIDAI's Authentication API error-handling guide says client-side validation of an
Aadhaar number "should be 12 digits and conform to Verhoeff algorithm".

Usage as a module:
    >>> from verhoeff import is_valid, check_digit
    >>> check_digit("236")
    '3'
    >>> is_valid("2363")
    True

Usage as a CLI:
    python3 verhoeff.py check 2363        # exit code 0 if valid, 1 if not
    python3 verhoeff.py digit 236         # prints the check digit to append

Standard library only.
"""

import sys

# Multiplication table d(j, k) of the dihedral group D5.
_D = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
    (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
    (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
    (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
    (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
    (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
    (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
    (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
    (9, 8, 7, 6, 5, 4, 3, 2, 1, 0),
)

# Permutation table p(pos mod 8, digit).
_P = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
    (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
    (8, 9, 1, 6, 0, 3, 4, 2, 7, 5),
    (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
    (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
    (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
    (7, 0, 4, 6, 9, 1, 3, 2, 5, 8),
)

# Inverse table inv(j).
_INV = (0, 4, 3, 2, 1, 5, 6, 7, 8, 9)


def _require_digits(number: str) -> str:
    if not isinstance(number, str):
        raise TypeError("number must be a str of ASCII digits")
    if not number or not (number.isascii() and number.isdigit()):
        raise ValueError("number must be a non-empty string of ASCII digits 0-9")
    return number


def _checksum(number: str) -> int:
    c = 0
    for i, ch in enumerate(reversed(number)):
        c = _D[c][_P[i % 8][int(ch)]]
    return c


def is_valid(number: str) -> bool:
    """Return True if the last digit of `number` is a correct Verhoeff check digit."""
    try:
        _require_digits(number)
    except (TypeError, ValueError):
        return False
    return _checksum(number) == 0


def check_digit(payload: str) -> str:
    """Return the Verhoeff check digit to append to `payload` (digits only)."""
    _require_digits(payload)
    c = 0
    for i, ch in enumerate(reversed(payload)):
        c = _D[c][_P[(i + 1) % 8][int(ch)]]
    return str(_INV[c])


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2 or argv[0] not in ("check", "digit"):
        print("usage: verhoeff.py check NUMBER | verhoeff.py digit PAYLOAD", file=sys.stderr)
        return 2
    cmd, value = argv
    if cmd == "check":
        ok = is_valid(value)
        print("valid" if ok else "invalid")
        return 0 if ok else 1
    try:
        print(check_digit(value))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
