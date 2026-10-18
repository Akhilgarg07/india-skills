#!/usr/bin/env python3
"""Validate a GST tax invoice (as JSON) against CGST Rule 46 particulars and common
GST invoicing rules, and decide CGST+SGST/UTGST vs IGST.

Checks:
  * supplier name/address/GSTIN (check character, state code)
  * invoice number: max 16 chars, only A-Z a-z 0-9 '-' '/' (rule 46(b)); date present
  * recipient GSTIN if registered; for unregistered recipients with taxable value
    >= Rs 50,000: name, address, delivery address, state name and code (rule 46(e))
  * place of supply present; tax type matches supplier state vs place of supply
    (IGST Act ss.7-8; SEZ supplies are always inter-state)
  * each line: description, HSN/SAC with enough digits for the supplier's turnover
    (Notification 78/2020-CT: 4 digits up to Rs 5 crore, 6 digits above), quantity and
    unit for goods, rate, and tax amounts that match taxable value x rate (+/- 1 paisa)
  * reverse-charge flag present (rule 46(p))
  * e-invoicing: IRN and QR expected when AATO > Rs 5 crore for B2B/export/SEZ invoices,
    unless the supplier is in an exempt category

Module usage:
    >>> from invoice_check import check_invoice, supply_type
    >>> supply_type("29", "27")
    'inter-state'
    >>> report = check_invoice(invoice_dict)   # {'ok': bool, 'errors': [...], 'warnings': [...]}

CLI usage:
    python3 invoice_check.py invoice.json
    python3 invoice_check.py --example > sample.json   # a correct sample invoice

Standard library only. Not tax advice.
"""

import json
import os
import re
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gstin_validate  # noqa: E402  (copy of indian-id-validation/scripts/gstin_validate.py)

FIVE_CRORE = Decimal("50000000")
UNREGISTERED_DETAIL_THRESHOLD = Decimal("50000")
# Union territories without legislature use UTGST instead of SGST (UTGST Act s.1(2)).
# 38 (Ladakh) and 97 (Other Territory) are included as "other territory".
UTGST_CODES = {"04", "25", "26", "31", "35", "38", "97"}  # TODO(verify): Ladakh (38) under UTGST
E_INVOICE_EXEMPT = {
    "sez_unit", "insurer", "banking_company", "financial_institution", "nbfc",
    "goods_transport_agency", "passenger_transport", "multiplex_cinema",
    "government_department", "local_authority",
}
INVOICE_NO_RE = re.compile(r"^[A-Za-z0-9/-]{1,16}$")
TOL = Decimal("0.01")


def _d(v):
    try:
        return Decimal(str(v).replace(",", ""))
    except (InvalidOperation, TypeError):
        return None


def supply_type(supplier_state: str, place_of_supply: str, *, sez=False, export=False) -> str:
    """'intra-state' or 'inter-state' from two GST state codes (IGST Act ss.7-8)."""
    if sez or export:
        return "inter-state"
    return "intra-state" if supplier_state == place_of_supply else "inter-state"


def state_tax_name(state_code: str) -> str:
    return "UTGST" if state_code in UTGST_CODES else "SGST"


def general_place_of_supply(kind, *, recipient_registered, recipient_state=None,
                            delivery_state=None, supplier_state=None):
    """General rules only (IGST Act s.10(1)(a)/(ca) for goods, s.12(2) for services).

    Many services have special rules (immovable property, events, transport, etc.);
    see references/place-of-supply.md. Returns a state code or None if undeterminable.
    """
    if kind == "goods":
        if recipient_registered:
            return delivery_state  # where movement of goods terminates
        # s.10(1)(ca): unregistered -> address recorded on invoice, else supplier location
        return recipient_state or supplier_state
    if kind == "services":
        if recipient_registered:
            return recipient_state
        return recipient_state or supplier_state
    raise ValueError("kind must be 'goods' or 'services'")


def _line_errors(i, line, supply, aato, b2b, errors, warnings):
    p = f"line {i}"
    if not str(line.get("description", "")).strip():
        errors.append(f"{p}: description is required (rule 46(h))")
    code = re.sub(r"\s", "", str(line.get("hsn", "")))
    is_service = code.startswith("99")
    if not code.isdigit() or len(code) not in (4, 6, 8):
        errors.append(f"{p}: HSN/SAC must be 4, 6 or 8 digits (got {code!r})")
    elif aato is not None:
        need = 6 if aato > FIVE_CRORE else 4
        if len(code) < need and (b2b or need == 6):
            errors.append(f"{p}: HSN/SAC needs at least {need} digits for AATO "
                          f"{'above' if need == 6 else 'up to'} Rs 5 crore (Notification 78/2020-CT)")
    if not is_service:
        if line.get("quantity") in (None, "") or not line.get("unit"):
            errors.append(f"{p}: goods need quantity and unit/UQC (rule 46(i))")
    taxable = _d(line.get("taxable_value"))
    rate = _d(line.get("rate"))
    if taxable is None or rate is None:
        errors.append(f"{p}: taxable_value and rate are required numbers (rule 46(k),(l))")
        return
    amounts = {k: _d(line.get(k, 0)) or Decimal(0) for k in ("cgst", "sgst", "utgst", "igst")}
    state_part = amounts["sgst"] + amounts["utgst"]
    if supply == "inter-state":
        if amounts["cgst"] or state_part:
            errors.append(f"{p}: inter-state supply must charge IGST only, not CGST/SGST")
        expected = (taxable * rate / 100).quantize(TOL, ROUND_HALF_UP)
        if abs(amounts["igst"] - expected) > TOL:
            errors.append(f"{p}: IGST should be {expected} (got {amounts['igst']})")
    else:
        if amounts["igst"]:
            errors.append(f"{p}: intra-state supply must charge CGST + SGST/UTGST, not IGST")
        half = (taxable * rate / 200).quantize(TOL, ROUND_HALF_UP)
        if abs(amounts["cgst"] - half) > TOL or abs(state_part - half) > TOL:
            errors.append(f"{p}: CGST and SGST/UTGST should each be {half} "
                          f"(got {amounts['cgst']} / {state_part})")


def check_invoice(inv: dict) -> dict:
    errors, warnings = [], []
    sup = inv.get("supplier", {}) or {}
    rec = inv.get("recipient", {}) or {}

    for f in ("name", "address", "gstin"):
        if not str(sup.get(f, "")).strip():
            errors.append(f"supplier.{f} is required (rule 46(a))")
    sup_state = None
    if sup.get("gstin"):
        g = gstin_validate.validate(sup["gstin"])
        if not g["valid"]:
            errors.append("supplier.gstin invalid: " + "; ".join(g["errors"]))
        else:
            sup_state = g["state_code"]

    no = str(inv.get("invoice_number", ""))
    if not INVOICE_NO_RE.match(no):
        errors.append("invoice_number must be 1-16 characters of letters, digits, '-' or '/', "
                      "unique for the financial year (rule 46(b))")
    if not inv.get("invoice_date"):
        errors.append("invoice_date is required (rule 46(c))")

    # "URP" (unregistered person) is how e-invoice JSON marks export / unregistered buyers.
    registered = bool(rec.get("gstin")) and str(rec["gstin"]).strip().upper() != "URP"
    if registered:
        g = gstin_validate.validate(rec["gstin"])
        if not g["valid"]:
            errors.append("recipient.gstin invalid: " + "; ".join(g["errors"]))
        for f in ("name", "address"):
            if not str(rec.get(f, "")).strip():
                errors.append(f"recipient.{f} is required for a registered recipient (rule 46(d))")

    lines = inv.get("lines") or []
    if not lines:
        errors.append("at least one line item is required")
    total_taxable = sum((_d(l.get("taxable_value")) or Decimal(0) for l in lines), Decimal(0))
    if not registered and total_taxable >= UNREGISTERED_DETAIL_THRESHOLD:
        for f in ("name", "address", "delivery_address", "state_code"):
            if not str(rec.get(f, "")).strip():
                errors.append(f"recipient.{f} is required for an unregistered recipient when "
                              "taxable value is Rs 50,000 or more (rule 46(e))")

    pos = str(inv.get("place_of_supply", "")).zfill(2) if inv.get("place_of_supply") else None
    if not pos:
        errors.append("place_of_supply (state code) is required (rule 46(n) for inter-state)")
    elif pos not in gstin_validate.STATE_CODES and pos != "96":
        errors.append(f"place_of_supply {pos!r} is not a GST state code (use 96 for exports)")

    export = bool(inv.get("export")) or pos == "96"
    sez = bool(rec.get("sez"))
    supply = supply_type(sup_state, pos, sez=sez, export=export) if sup_state and pos else None
    if supply and inv.get("supply_type") and inv["supply_type"] != supply:
        errors.append(f"supply_type says {inv['supply_type']!r} but supplier state {sup_state} "
                      f"and place of supply {pos} make it {supply!r}")

    if "reverse_charge" not in inv:
        errors.append("reverse_charge (true/false) must be stated (rule 46(p))")

    aato = _d(inv.get("supplier_aato")) if inv.get("supplier_aato") is not None else None
    b2b = registered or sez or export
    for i, line in enumerate(lines, 1):
        if supply:
            _line_errors(i, line, supply, aato, b2b, errors, warnings)

    if export and not inv.get("export_endorsement"):
        warnings.append("export / SEZ invoices must carry the endorsement 'SUPPLY MEANT FOR EXPORT/"
                        "SUPPLY TO SEZ UNIT OR SEZ DEVELOPER FOR AUTHORISED OPERATIONS ON PAYMENT OF "
                        "INTEGRATED TAX' (or '... UNDER BOND OR LETTER OF UNDERTAKING WITHOUT PAYMENT "
                        "OF INTEGRATED TAX')")
    if supply == "intra-state" and sup_state in UTGST_CODES:
        warnings.append(f"state code {sup_state} is a UT without legislature: label the state "
                        "component UTGST, not SGST")

    exempt = sup.get("e_invoice_exempt_category") in E_INVOICE_EXEMPT
    if aato is None:
        warnings.append("supplier_aato not given: cannot check HSN digits or e-invoicing applicability")
    elif aato > FIVE_CRORE and b2b and not exempt:
        if not inv.get("irn") or not inv.get("qr_code"):
            errors.append("supplier AATO exceeds Rs 5 crore: B2B/export/SEZ invoice needs an IRN from "
                          "the IRP and the signed QR code (rule 48(4)); otherwise it is not a valid invoice")
        if aato >= Decimal("100000000"):
            warnings.append("AATO is Rs 10 crore or more: report to the IRP within 30 days of the "
                            "invoice date or IRN generation is refused (from 1 Apr 2025)")

    return {"ok": not errors, "supply_type": supply, "errors": errors, "warnings": warnings}


EXAMPLE = {
    "invoice_number": "INV/2026-27/0042",
    "invoice_date": "2026-10-18",
    "supplier": {"name": "Example Software Pvt Ltd", "address": "Bengaluru, Karnataka 560001",
                 "gstin": "29AAACE1234F1Z2"},
    "supplier_aato": "30000000",
    "recipient": {"name": "Example Buyer Ltd", "address": "Mumbai, Maharashtra 400001",
                  "gstin": "27AAACB5678K1ZA"},
    "place_of_supply": "27",
    "supply_type": "inter-state",
    "reverse_charge": False,
    "lines": [{"description": "Software development services", "hsn": "998314",
               "taxable_value": "100000.00", "rate": "18", "igst": "18000.00"}],
    "total_taxable_value": "100000.00",
    "total_tax": "18000.00",
    "total": "118000.00",
}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["--example"]:
        print(json.dumps(EXAMPLE, indent=2))
        return 0
    if len(argv) != 1:
        print("usage: invoice_check.py INVOICE.json | invoice_check.py --example", file=sys.stderr)
        return 2
    with open(argv[0], encoding="utf-8") as fh:
        inv = json.load(fh)
    r = check_invoice(inv)
    print(f"supply type: {r['supply_type']}")
    for e in r["errors"]:
        print(f"ERROR   {e}")
    for w in r["warnings"]:
        print(f"WARNING {w}")
    print("OK" if r["ok"] else f"{len(r['errors'])} error(s)")
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
