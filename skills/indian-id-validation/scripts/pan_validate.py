#!/usr/bin/env python3
"""PAN (Permanent Account Number) and TAN format validation.

PAN structure (Income Tax Department, "How PAN is formed"):
  chars 1-3  alphabetic series AAA-ZZZ
  char  4    status of holder (see HOLDER_TYPES)
  char  5    first letter of surname (individuals) or of the name (others)
  chars 6-9  sequential number 0001-9999
  char  10   alphabetic check digit (algorithm not published -> not checked here)

TAN structure (Income Tax Department, "What is TAN?"):
  chars 1-4 letters (jurisdiction code + initial of holder's name),
  chars 5-9 digits (00001-99999), char 10 alphabetic check digit.

Format-valid does not mean the PAN/TAN exists or belongs to this person; verify
through the Income Tax Department / an authorised verification service.

Module usage:
    >>> from pan_validate import validate_pan
    >>> validate_pan("ALWPG5809L")["holder_type"]
    'Individual'

CLI usage:
    python3 pan_validate.py ALWPG5809L
    python3 pan_validate.py --tan DELM12345L
    python3 pan_validate.py --json ALWPG5809L

Standard library only.
"""

import json
import re
import sys

HOLDER_TYPES = {
    "A": "Association of Persons (AOP)",
    "B": "Body of Individuals (BOI)",
    "C": "Company",
    "F": "Firm / Limited Liability Partnership",
    "G": "Government Agency",
    "H": "Hindu Undivided Family (HUF)",
    "J": "Artificial Juridical Person",
    "L": "Local Authority",
    "P": "Individual",
    "T": "Trust",
}

PAN_RE = re.compile(r"^[A-Z]{3}[ABCFGHJLPT][A-Z][0-9]{4}[A-Z]$")
TAN_RE = re.compile(r"^[A-Z]{4}[0-9]{5}[A-Z]$")


def normalize(value: str) -> str:
    """Trim and uppercase. Internal spaces are NOT removed: a PAN never contains them."""
    if not isinstance(value, str):
        raise TypeError("value must be a str")
    return value.strip().upper()


def validate_pan(value: str) -> dict:
    pan = normalize(value)
    errors = []
    if len(pan) != 10:
        errors.append(f"must be 10 characters (got {len(pan)})")
    elif not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", pan):
        errors.append("must be 5 letters, 4 digits, 1 letter (e.g. ABCPE1234F)")
    elif pan[3] not in HOLDER_TYPES:
        errors.append(f"4th character '{pan[3]}' is not a known holder-status code "
                      f"({''.join(sorted(HOLDER_TYPES))})")
    elif pan[5:9] == "0000":
        errors.append("digits 6-9 run from 0001 to 9999; 0000 is not issued")
    ok = not errors
    return {
        "input": value,
        "normalized": pan,
        "valid": ok,
        "errors": errors,
        "holder_type": HOLDER_TYPES.get(pan[3]) if ok else None,
        "is_individual": (pan[3] == "P") if ok else None,
    }


def validate_tan(value: str) -> dict:
    tan = normalize(value)
    errors = []
    if len(tan) != 10:
        errors.append(f"must be 10 characters (got {len(tan)})")
    elif not TAN_RE.match(tan):
        errors.append("must be 4 letters, 5 digits, 1 letter (e.g. DELM12345L)")
    elif tan[4:9] == "00000":
        errors.append("digits 5-9 run from 00001 to 99999; 00000 is not issued")
    return {"input": value, "normalized": tan, "valid": not errors, "errors": errors}


def is_valid_pan(value: str) -> bool:
    return validate_pan(value)["valid"]


def is_valid_tan(value: str) -> bool:
    return validate_tan(value)["valid"]


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    as_json = "--json" in argv
    tan_mode = "--tan" in argv
    values = [a for a in argv if a not in ("--json", "--tan")]
    if not values:
        print("usage: pan_validate.py [--tan] [--json] VALUE [VALUE ...]", file=sys.stderr)
        return 2
    fn = validate_tan if tan_mode else validate_pan
    results = [fn(v) for v in values]
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            extra = f" ({r['holder_type']})" if r.get("holder_type") else ""
            status = "valid" + extra if r["valid"] else "invalid: " + "; ".join(r["errors"])
            print(f"{r['normalized']}  {status}")
    return 0 if all(r["valid"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
