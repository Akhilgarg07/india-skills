#!/usr/bin/env python3
"""Aadhaar number FORMAT + CHECKSUM validation, and masking.

This module never returns, prints or raises with the full Aadhaar number.
Results only ever contain the masked form (last four digits visible).

What it checks (and nothing more):
  * exactly 12 ASCII digits after removing spaces/hyphens, and
  * the last digit is a valid Verhoeff check digit (UIDAI API error-handling guide).

A passing result does NOT mean the number was issued by UIDAI or belongs to the
person in front of you. Only UIDAI authentication / offline verification can do that.

Module usage:
    >>> from aadhaar_validate import validate, mask
    >>> r = validate(user_input)        # dict: valid, errors, masked
    >>> mask(user_input)                # 'XXXX XXXX 1234'

CLI usage (reads from stdin so the number never lands in shell history):
    printf '%s' "$AADHAAR" | python3 aadhaar_validate.py
    python3 aadhaar_validate.py --mask < file_with_one_number_per_line

Standard library only.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verhoeff  # noqa: E402

_SEPARATORS = " - "


def _digits_only(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("Aadhaar value must be a str")
    return "".join(ch for ch in value.strip() if ch not in _SEPARATORS)


def mask(value: str, mask_char: str = "X") -> str:
    """Return the masked form 'XXXX XXXX 1234' (only the last four digits visible).

    Works on any input; if it is not 12 digits the whole value is masked so that
    nothing partial is leaked.
    """
    digits = _digits_only(value)
    if len(digits) == 12 and digits.isascii() and digits.isdigit():
        return f"{mask_char * 4} {mask_char * 4} {digits[-4:]}"
    return mask_char * 4 + " " + mask_char * 4 + " " + mask_char * 4


def validate(value: str) -> dict:
    """Validate format and Verhoeff checksum. Never includes the full number in output."""
    errors = []
    digits = _digits_only(value)
    if digits and not (digits.isascii() and digits.isdigit()):
        errors.append("must contain only digits (spaces or hyphens between groups are allowed)")
    elif len(digits) != 12:
        errors.append(f"must be exactly 12 digits (got {len(digits)})")
    elif not verhoeff.is_valid(digits):
        errors.append("checksum (Verhoeff) does not match; likely a typo")
    return {"valid": not errors, "errors": errors, "masked": mask(value)}


def is_valid(value: str) -> bool:
    return validate(value)["valid"]


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if any(a not in ("--mask",) for a in argv):
        print("refusing to read Aadhaar numbers from command-line arguments "
              "(they end up in shell history); pipe them on stdin instead", file=sys.stderr)
        return 2
    only_mask = "--mask" in argv
    all_ok = True
    for line in sys.stdin:
        if not line.strip():
            continue
        if only_mask:
            print(mask(line))
            continue
        r = validate(line)
        all_ok &= r["valid"]
        status = "valid" if r["valid"] else "invalid: " + "; ".join(r["errors"])
        print(f"{r['masked']}  {status}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
