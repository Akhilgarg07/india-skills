#!/usr/bin/env python3
"""Build, parse and validate UPI payment links (upi://pay?...) and VPAs.

Parameter names follow NPCI's "UPI Linking Specifications" (deep linking / QR):
  pa  payee VPA (mandatory)          pn  payee name (mandatory)
  am  amount, decimal (mandatory for dynamic links/QRs; omit to let the payer enter it)
  cu  currency, only "INR"           tn  short transaction note
  tr  transaction reference (order/bill id; mandatory for merchant / dynamic links)
  mc  merchant category code         tid PSP-generated transaction id
  mam minimum amount                 url link to transaction details (http/https)
  mode initiation mode (2 digits)    sign/orgid/mid/msid/mtid  signed-intent fields

A UPI QR code is simply this same URI encoded as a QR image.

A link is a *request*. Opening it proves nothing about payment. Always confirm payment
status server-side (PSP / payment gateway status API or webhook).

Module usage:
    >>> from upi_link import build_upi_link, parse_upi_link, validate_vpa
    >>> build_upi_link("merchant@okbank", "Asha Stores", am="149.50", tr="ORD1001", tn="Order 1001")
    'upi://pay?pa=merchant@okbank&pn=Asha%20Stores&am=149.50&cu=INR&tn=Order%201001&tr=ORD1001'
    >>> parse_upi_link("upi://pay?pa=a.b@ybl&pn=A%20B&am=10")["params"]["pn"]
    'A B'

CLI usage:
    python3 upi_link.py build --pa merchant@okbank --pn "Asha Stores" --am 149.50 --tr ORD1001
    python3 upi_link.py parse "upi://pay?pa=merchant@okbank&pn=Asha%20Stores&am=149.50"
    python3 upi_link.py vpa someone@okaxis

Standard library only.
"""

import argparse
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from urllib.parse import parse_qsl, quote, urlsplit

# Pragmatic VPA check: "<handle>@<psp>". NPCI does not publish a public character-level
# grammar (TODO(verify)); this accepts the forms PSPs issue and rejects obvious garbage.
VPA_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,255}@[A-Za-z][A-Za-z0-9]{1,63}$")
AMOUNT_RE = re.compile(r"^\d{1,9}(\.\d{1,2})?$")
MODE_VALUES = {"00", "01", "02", "04", "05", "06", "07", "08", "15"}
PARAM_ORDER = ("pa", "pn", "mc", "tid", "tr", "tn", "am", "mam", "cu", "url", "mode",
               "orgid", "mid", "msid", "mtid", "sign")
KNOWN = set(PARAM_ORDER) | {"query"}


def validate_vpa(vpa: str) -> dict:
    errors = []
    if not isinstance(vpa, str) or not vpa:
        errors.append("VPA is empty")
    elif vpa != vpa.strip():
        errors.append("VPA has leading/trailing spaces")
    elif vpa.count("@") != 1:
        errors.append("VPA must contain exactly one '@' (handle@psp)")
    elif not VPA_RE.match(vpa):
        errors.append("VPA must look like name@psp: letters, digits, '.', '_' or '-' before '@', "
                      "letters/digits after it")
    return {"vpa": vpa, "valid": not errors, "errors": errors,
            "psp_handle": vpa.split("@", 1)[1].lower() if not errors else None}


def _check_amount(name, value, errors):
    if not AMOUNT_RE.match(value):
        errors.append(f"{name} must be a decimal with at most 2 decimal places, e.g. 149.50 (got {value!r})")
        return None
    try:
        d = Decimal(value)
    except InvalidOperation:
        errors.append(f"{name} is not a number")
        return None
    if d <= 0:
        errors.append(f"{name} must be greater than zero")
    return d


def validate_params(p: dict, *, dynamic=False) -> list:
    errors = []
    for req in ("pa", "pn"):
        if not p.get(req):
            errors.append(f"'{req}' is mandatory")
    if p.get("pa"):
        errors += [f"pa: {e}" for e in validate_vpa(p["pa"])["errors"]]
    am = p.get("am")
    if am is not None:
        _check_amount("am", am, errors)
    elif dynamic:
        errors.append("'am' is mandatory for a dynamic (per-order) link/QR")
    if p.get("mam") is not None and p.get("mam") not in ("", "null"):
        mam = _check_amount("mam", p["mam"], errors)
        if mam is not None and am and AMOUNT_RE.match(am) and mam > Decimal(am):
            errors.append("mam (minimum amount) cannot exceed am")
    if p.get("cu", "INR") != "INR":
        errors.append("cu: only INR is supported")
    if dynamic and not p.get("tr"):
        errors.append("'tr' (transaction/order reference) is mandatory for merchant/dynamic links")
    if p.get("url") and not re.match(r"^https?://", p["url"]):
        errors.append("url must start with http:// or https://")
    if p.get("mode") and p["mode"] not in MODE_VALUES:
        errors.append(f"mode must be one of {sorted(MODE_VALUES)}")
    if p.get("tn") and len(p["tn"]) > 80:
        errors.append("tn is meant to be a short note; keep it under ~80 characters "
                      "(apps truncate long notes)")
    return errors


def build_upi_link(pa, pn, *, am=None, cu="INR", tn=None, tr=None, mc=None, tid=None,
                   url=None, mode=None, mam=None, dynamic=None, **extra) -> str:
    """Return a upi://pay URI. Raises ValueError listing every problem found."""
    if am is not None:
        am = str(am)
    params = {"pa": pa, "pn": pn, "am": am, "cu": cu, "tn": tn, "tr": tr, "mc": mc,
              "tid": tid, "url": url, "mode": mode, "mam": None if mam is None else str(mam)}
    params.update({k: v for k, v in extra.items() if v is not None})
    params = {k: v for k, v in params.items() if v is not None}
    if dynamic is None:
        dynamic = am is not None and tr is not None
    errors = validate_params(params, dynamic=dynamic)
    unknown = set(params) - KNOWN
    if unknown:
        errors.append(f"unknown parameter(s) {sorted(unknown)}")
    if errors:
        raise ValueError("; ".join(errors))
    # Fixed, readable order; spaces as %20 (not '+'), '@' left as-is in the VPA.
    order = ["pa", "pn", "am", "cu", "tn", "tr", "mc", "tid", "mam", "url", "mode"]
    keys = order + [k for k in params if k not in order]
    parts = [f"{k}={quote(params[k], safe='@.-_:/' if k in ('pa', 'url') else '@.-_')}"
             for k in keys if k in params]
    return "upi://pay?" + "&".join(parts)


def parse_upi_link(uri: str, *, dynamic=False) -> dict:
    """Parse and validate a upi://pay URI. Returns {'valid', 'errors', 'params'}."""
    errors = []
    s = urlsplit(uri.strip())
    if s.scheme.lower() != "upi" or s.netloc.lower() != "pay":
        errors.append("must start with upi://pay?")
    pairs = parse_qsl(s.query, keep_blank_values=True)
    params = {}
    for k, v in pairs:
        if k in params:
            errors.append(f"duplicate parameter '{k}'")
        params[k] = v
    errors += validate_params(params, dynamic=dynamic)
    return {"valid": not errors, "errors": errors, "params": params}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="UPI deep link / QR payload helper")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    for k in ("pa", "pn", "am", "tn", "tr", "mc", "tid", "url", "mode", "mam"):
        b.add_argument(f"--{k}", required=k in ("pa", "pn"))
    b.add_argument("--cu", default="INR")
    p = sub.add_parser("parse")
    p.add_argument("uri")
    p.add_argument("--dynamic", action="store_true", help="require am and tr")
    v = sub.add_parser("vpa")
    v.add_argument("vpa")
    a = ap.parse_args(argv)

    if a.cmd == "build":
        kw = {k: getattr(a, k) for k in ("am", "tn", "tr", "mc", "tid", "url", "mode", "mam")}
        try:
            print(build_upi_link(a.pa, a.pn, cu=a.cu, **kw))
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        return 0
    if a.cmd == "parse":
        r = parse_upi_link(a.uri, dynamic=a.dynamic)
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 0 if r["valid"] else 1
    r = validate_vpa(a.vpa)
    print(json.dumps(r, indent=2))
    return 0 if r["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
