#!/usr/bin/env python3
"""GSTIN (GST Identification Number) format and check-character validation.

Structure (CGST Rules, rule 10 / CBIC registration flier):
  2 chars  State code
  10 chars PAN (or, for tax deductors, the TAN)
  2 chars  entity code
  1 char   checksum character

Check character: the mod-36 weighted algorithm implemented in check_char().
GSTN does not publish it in a rule or notification; it reproduces the check
character of every real, published GSTIN we tested (see references/sources.md).

Format-valid does not mean the GSTIN is registered or active. Use the GST portal
"Search Taxpayer" service (or a GSP/API provider) to confirm status.

Module usage:
    >>> from gstin_validate import validate, check_char
    >>> validate("27AABCE6624L1ZG")["state_name"]
    'Maharashtra'

CLI usage:
    python3 gstin_validate.py 27AABCE6624L1ZG 29AABCE6624L1ZC
    python3 gstin_validate.py --json 27AABCE6624L1ZG

Standard library only.
"""

import json
import re
import sys

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# GST state codes. Source: GST state code list (Nagaland Commercial Taxes Dept.)
# and GSTN e-way bill / e-invoice master codes for 97 and 99.
STATE_CODES = {
    "01": "Jammu and Kashmir",
    "02": "Himachal Pradesh",
    "03": "Punjab",
    "04": "Chandigarh",
    "05": "Uttarakhand",
    "06": "Haryana",
    "07": "Delhi",
    "08": "Rajasthan",
    "09": "Uttar Pradesh",
    "10": "Bihar",
    "11": "Sikkim",
    "12": "Arunachal Pradesh",
    "13": "Nagaland",
    "14": "Manipur",
    "15": "Mizoram",
    "16": "Tripura",
    "17": "Meghalaya",
    "18": "Assam",
    "19": "West Bengal",
    "20": "Jharkhand",
    "21": "Odisha",
    "22": "Chhattisgarh",
    "23": "Madhya Pradesh",
    "24": "Gujarat",
    "25": "Daman and Diu",
    "26": "Dadra and Nagar Haveli and Daman and Diu",
    "27": "Maharashtra",
    "28": "Andhra Pradesh (before division)",
    "29": "Karnataka",
    "30": "Goa",
    "31": "Lakshadweep",
    "32": "Kerala",
    "33": "Tamil Nadu",
    "34": "Puducherry",
    "35": "Andaman and Nicobar Islands",
    "36": "Telangana",
    "37": "Andhra Pradesh",
    "38": "Ladakh",
    "97": "Other Territory",
    "99": "Centre Jurisdiction / Other Country",  # TODO(verify): label differs between sources
}

# Codes that only ever applied before a reorganisation; GSTINs may still appear in old data.
HISTORICAL_CODES = {
    "25": "Daman and Diu used code 25 from July 2017 to 26 Jan 2020; merged UT uses 26",
    "28": "code 28 is listed for Andhra Pradesh before division; Andhra Pradesh now uses 37",
}

_PAN_RE = re.compile(r"^[A-Z]{3}[ABCFGHJLPT][A-Z][0-9]{4}[A-Z]$")
_TAN_RE = re.compile(r"^[A-Z]{4}[0-9]{5}[A-Z]$")


def normalize(value: str) -> str:
    """Trim and uppercase. Internal spaces are kept so they fail validation visibly."""
    if not isinstance(value, str):
        raise TypeError("value must be a str")
    return value.strip().upper()


def check_char(first14: str) -> str:
    """Return the expected 15th (check) character for the first 14 characters."""
    first14 = normalize(first14)
    if len(first14) != 14 or any(c not in ALPHABET for c in first14):
        raise ValueError("need exactly 14 characters from 0-9 / A-Z")
    total = 0
    for i, ch in enumerate(first14):
        product = ALPHABET.index(ch) * (2 if i % 2 else 1)
        total += product // 36 + product % 36
    return ALPHABET[(36 - total % 36) % 36]


def validate(value: str) -> dict:
    g = normalize(value)
    errors, warnings = [], []
    result = {"input": value, "normalized": g, "valid": False, "errors": errors,
              "warnings": warnings, "state_code": None, "state_name": None,
              "pan": None, "tan": None, "registration_kind": None}

    if len(g) != 15:
        errors.append(f"must be 15 characters (got {len(g)})")
        return result
    if any(c not in ALPHABET for c in g):
        errors.append("may contain only digits 0-9 and letters A-Z")
        return result

    code = g[:2]
    result["state_code"] = code
    if code not in STATE_CODES:
        errors.append(f"'{code}' is not a GST state code")
    else:
        result["state_name"] = STATE_CODES[code]
        if code in HISTORICAL_CODES:
            warnings.append(HISTORICAL_CODES[code])

    body = g[2:12]
    if _PAN_RE.match(body):
        result["registration_kind"] = "pan-based"
        result["pan"] = body
    elif _TAN_RE.match(body):
        result["registration_kind"] = "tan-based (tax deductor)"
        result["tan"] = body
    else:
        result["registration_kind"] = "other"
        warnings.append("characters 3-12 are neither a PAN nor a TAN; this can be a "
                        "special registration (e.g. UIN or non-resident) - only the "
                        "check character was verified")

    expected = check_char(g[:14])
    if g[14] != expected:
        errors.append(f"check character should be '{expected}', got '{g[14]}' (likely a typo)")

    result["valid"] = not errors
    return result


def is_valid(value: str) -> bool:
    return validate(value)["valid"]


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    as_json = "--json" in argv
    values = [a for a in argv if a != "--json"]
    if not values:
        print("usage: gstin_validate.py [--json] GSTIN [GSTIN ...]", file=sys.stderr)
        return 2
    results = [validate(v) for v in values]
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            if r["valid"]:
                status = f"valid ({r['state_name']}, {r['registration_kind']})"
            else:
                status = "invalid: " + "; ".join(r["errors"])
            print(f"{r['normalized']}  {status}")
            for w in r["warnings"]:
                print(f"    warning: {w}")
    return 0 if all(r["valid"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
