#!/usr/bin/env python3
"""IFSC (Indian Financial System Code) format validation.

RBI NEFT FAQ: IFSC is an 11-character alphanumeric code; the first 4 alphabetic
characters identify the bank, the 5th character is 0 (zero), and the last 6
characters identify the branch.

Format-valid does not mean the branch exists. Check against RBI's bank-wise IFSC
list (or a maintained dataset derived from it) when existence matters.

Module usage:
    >>> from ifsc_validate import validate
    >>> validate("RBIS0NDPA01")["bank_code"]
    'RBIS'

CLI usage:
    python3 ifsc_validate.py RBIS0NDPA01 RBIS0GWPA01
    python3 ifsc_validate.py --json RBIS0NDPA01

Standard library only.
"""

import json
import re
import sys

IFSC_RE = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$")


def normalize(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("value must be a str")
    return value.strip().upper()


def validate(value: str) -> dict:
    code = normalize(value)
    errors, hints = [], []
    if len(code) != 11:
        errors.append(f"must be 11 characters (got {len(code)})")
    elif not re.fullmatch(r"[A-Z0-9]{11}", code):
        errors.append("may contain only letters A-Z and digits 0-9")
    else:
        if not code[:4].isalpha():
            errors.append("first 4 characters (bank code) must be letters")
        if code[4] != "0":
            errors.append(f"5th character must be the digit 0 (got '{code[4]}')")
            if code[4] == "O":
                hints.append("5th character is the letter O; it should be the digit zero")
    ok = not errors and bool(IFSC_RE.match(code))
    return {
        "input": value,
        "normalized": code,
        "valid": ok,
        "errors": errors,
        "hints": hints,
        "bank_code": code[:4] if ok else None,
        "branch_code": code[5:] if ok else None,
    }


def is_valid(value: str) -> bool:
    return validate(value)["valid"]


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    as_json = "--json" in argv
    values = [a for a in argv if a != "--json"]
    if not values:
        print("usage: ifsc_validate.py [--json] IFSC [IFSC ...]", file=sys.stderr)
        return 2
    results = [validate(v) for v in values]
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            status = (f"valid (bank {r['bank_code']}, branch {r['branch_code']})" if r["valid"]
                      else "invalid: " + "; ".join(r["errors"] + r["hints"]))
            print(f"{r['normalized']}  {status}")
    return 0 if all(r["valid"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
