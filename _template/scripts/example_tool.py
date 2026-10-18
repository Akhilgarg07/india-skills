#!/usr/bin/env python3
"""One-line summary of what this tool checks or computes.

Rules encoded (cite each in references/sources.md):
  * rule 1 ...
  * rule 2 ...

Module usage:
    >>> from example_tool import validate
    >>> validate("ABC123")["valid"]
    True

CLI usage:
    python3 example_tool.py ABC123
    python3 example_tool.py --json ABC123

Exit codes: 0 = all valid, 1 = any invalid, 2 = usage error.
Standard library only.
"""

import json
import re
import sys

PATTERN = re.compile(r"^[A-Z]{3}[0-9]{3}$")   # replace with your rule


def normalize(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("value must be a str")
    return value.strip().upper()


def validate(value: str) -> dict:
    v = normalize(value)
    errors = []
    if not PATTERN.match(v):
        errors.append("must be 3 letters followed by 3 digits")   # specific, actionable messages
    return {"input": value, "normalized": v, "valid": not errors, "errors": errors}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    as_json = "--json" in argv
    values = [a for a in argv if a != "--json"]
    if not values:
        print("usage: example_tool.py [--json] VALUE [VALUE ...]", file=sys.stderr)
        return 2
    results = [validate(v) for v in values]
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"{r['normalized']}  {'valid' if r['valid'] else 'invalid: ' + '; '.join(r['errors'])}")
    return 0 if all(r["valid"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
