#!/usr/bin/env python3
"""Indian PIN code (Postal Index Number) format validation.

Structure (Department of Posts, via PIB release):
  * 6 digits. There are 9 PIN regions; the first digit indicates the region.
    Digits 1-8 are geographical regions; 9 is reserved for the Army Postal Service.
  * First 2 digits: sub-region / postal circle. First 3 digits: sorting / revenue
    district. Last 3 digits: the delivery post office.

A 6-digit string starting 1-9 is format-valid. That does not mean the PIN code
exists. For existence and PIN -> district/state lookups, use India Post's
All India Pincode Directory (published on data.gov.in).

Module usage:
    >>> from pincode_validate import validate
    >>> validate("110001")["region_digit"]
    '1'

CLI usage:
    python3 pincode_validate.py 110001 "560 001"
    python3 pincode_validate.py --json 110001

Standard library only.
"""

import json
import sys


def normalize(value: str) -> str:
    """Trim and remove a single internal space (PINs are often written '560 001')."""
    if not isinstance(value, str):
        raise TypeError("value must be a str")
    v = value.strip()
    if len(v) == 7 and v[3] == " ":
        v = v[:3] + v[4:]
    return v


def validate(value: str) -> dict:
    pin = normalize(value)
    errors = []
    if not (pin.isascii() and pin.isdigit()):
        errors.append("must contain only digits")
    elif len(pin) != 6:
        errors.append(f"must be exactly 6 digits (got {len(pin)})")
    elif pin[0] == "0":
        errors.append("first digit is the PIN region (1-9); 0 is not used")
    ok = not errors
    return {
        "input": value,
        "normalized": pin if ok else None,
        "valid": ok,
        "errors": errors,
        "region_digit": pin[0] if ok else None,
        "sub_region": pin[:2] if ok else None,
        "sorting_district": pin[:3] if ok else None,
        "is_army_postal_service": (pin[0] == "9") if ok else None,
    }


def is_valid(value: str) -> bool:
    return validate(value)["valid"]


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    as_json = "--json" in argv
    values = [a for a in argv if a != "--json"]
    if not values:
        print("usage: pincode_validate.py [--json] PIN [PIN ...]", file=sys.stderr)
        return 2
    results = [validate(v) for v in values]
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            if r["valid"]:
                note = " (Army Postal Service)" if r["is_army_postal_service"] else ""
                status = f"valid, region {r['region_digit']}{note}"
            else:
                status = "invalid: " + "; ".join(r["errors"])
            print(f"{r['input']!r}  {status}")
    return 0 if all(r["valid"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
