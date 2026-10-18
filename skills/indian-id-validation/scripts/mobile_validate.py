#!/usr/bin/env python3
"""Indian mobile number format validation and normalisation to E.164.

Rules used:
  * The National Significant Number is 10 digits for mobile services
    (DoT National Numbering Plan 2003).
  * Mobile numbering is allocated from level 9 and sub-levels of 7, 8 and 6
    (TRAI recommendations, 29 May 2020), so the first digit is 6, 7, 8 or 9.
  * Accepted prefixes: +91, 0091, 91 (12 digits total), or a single trunk 0.

This is a format check. It cannot tell you whether a number is active, which
operator it is on (mobile number portability makes prefixes unreliable), or
whether the user owns it. Use an OTP to prove ownership.

Module usage:
    >>> from mobile_validate import validate
    >>> validate("+91 98765 43210")["e164"]
    '+919876543210'

CLI usage:
    python3 mobile_validate.py "+91 98765 43210" 09876543210
    python3 mobile_validate.py --json 9876543210

Standard library only.
"""

import json
import sys

_STRIP = " -(). "


def normalize(value: str) -> str:
    """Remove spaces, hyphens, dots and brackets; keep a leading '+'."""
    if not isinstance(value, str):
        raise TypeError("value must be a str")
    return "".join(ch for ch in value.strip() if ch not in _STRIP)


def validate(value: str) -> dict:
    raw = normalize(value)
    errors = []
    national = None
    digits = raw[1:] if raw.startswith("+") else raw

    if not (digits.isascii() and digits.isdigit()):
        errors.append("may contain only digits, spaces, hyphens, brackets and a leading +")
    else:
        if raw.startswith("+"):
            if digits.startswith("91") and len(digits) == 12:
                national = digits[2:]
            else:
                errors.append("international form must be +91 followed by 10 digits")
        elif digits.startswith("0091") and len(digits) == 14:
            national = digits[4:]
        elif digits.startswith("91") and len(digits) == 12:
            national = digits[2:]
        elif digits.startswith("0") and len(digits) == 11:
            national = digits[1:]
        elif len(digits) == 10:
            national = digits
        else:
            errors.append(f"expected 10 digits, optionally prefixed by +91 / 91 / 0 (got {len(digits)} digits)")

    if national is not None and national[0] not in "6789":
        errors.append(f"Indian mobile numbers start with 6, 7, 8 or 9 (got '{national[0]}')")
        national = None

    ok = not errors
    return {
        "input": value,
        "valid": ok,
        "errors": errors,
        "national": national if ok else None,
        "e164": f"+91{national}" if ok else None,
    }


def is_valid(value: str) -> bool:
    return validate(value)["valid"]


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    as_json = "--json" in argv
    values = [a for a in argv if a != "--json"]
    if not values:
        print("usage: mobile_validate.py [--json] NUMBER [NUMBER ...]", file=sys.stderr)
        return 2
    results = [validate(v) for v in values]
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            status = f"valid -> {r['e164']}" if r["valid"] else "invalid: " + "; ".join(r["errors"])
            print(f"{r['input']!r}  {status}")
    return 0 if all(r["valid"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
