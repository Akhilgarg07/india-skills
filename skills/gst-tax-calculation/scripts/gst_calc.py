#!/usr/bin/env python3
"""GST calculator: exclusive / inclusive pricing, CGST+SGST vs IGST split,
reverse charge, and rupee rounding as in section 170 of the CGST Act.

All money is handled with decimal.Decimal and rounded half-up to paise per line.
Never use binary floats for tax.

Module usage:
    >>> from gst_calc import calculate
    >>> r = calculate("100000", 18, inter_state=True)
    >>> str(r["igst"]), str(r["total"])
    ('18000.00', '118000.00')
    >>> r = calculate("118000", 18, inclusive=True)
    >>> str(r["taxable_value"]), str(r["cgst"]), str(r["sgst"])
    ('100000.00', '9000.00', '9000.00')

CLI usage:
    python3 gst_calc.py 100000 --rate 18                  # intra-state, exclusive
    python3 gst_calc.py 118000 --rate 18 --inclusive --inter-state
    python3 gst_calc.py 5000 --rate 18 --reverse-charge
    python3 gst_calc.py 999.99 --rate 5 --round-total --json

Rates: current rates are those notified from 22 Sep 2025 (see references/rate-slabs.md).
Other rates (12, 28, ...) still appear on older invoices; they are accepted with a
warning unless strict=True / --strict.

Standard library only. Not tax advice.
"""

import argparse
import json
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

PAISE = Decimal("0.01")
RUPEE = Decimal("1")

# GST (IGST-equivalent) rates in force for most supplies from 22 September 2025.
CURRENT_RATES = (Decimal("0"), Decimal("0.25"), Decimal("1.5"), Decimal("3"),
                 Decimal("5"), Decimal("18"), Decimal("40"))


def _d(value, what="amount") -> Decimal:
    if isinstance(value, float):
        value = repr(value)  # avoid binary-float artefacts such as 0.1 + 0.2
    try:
        d = Decimal(str(value).replace(",", "").replace("₹", "").strip())
    except InvalidOperation:
        raise ValueError(f"{what} {value!r} is not a number") from None
    if not d.is_finite():
        raise ValueError(f"{what} must be finite")
    return d


def to_paise(x: Decimal) -> Decimal:
    return x.quantize(PAISE, rounding=ROUND_HALF_UP)


def round_rupee(amount) -> Decimal:
    """Section 170 CGST Act: 50 paise or more -> next rupee; less than 50 paise -> ignored."""
    amount = _d(amount)
    sign = -1 if amount < 0 else 1
    return sign * abs(amount).quantize(RUPEE, rounding=ROUND_HALF_UP)


def check_rate(rate, strict=False):
    """Return (rate as Decimal, warnings). Raise ValueError for impossible rates."""
    r = _d(rate, "rate")
    if r < 0 or r > 40:
        raise ValueError("GST rate must be between 0 and 40 per cent")
    warnings = []
    if r not in CURRENT_RATES:
        msg = (f"{r}% is not a GST rate notified from 22 Sep 2025 "
               f"({', '.join(str(x) for x in CURRENT_RATES)}); "
               "OK only for older invoices or special notifications")
        if strict:
            raise ValueError(msg)
        warnings.append(msg)
    return r, warnings


def calculate(amount, rate, *, inclusive=False, inter_state=False,
              reverse_charge=False, round_total=False, strict=False) -> dict:
    """Compute GST for one line.

    amount        taxable value (exclusive) or tax-inclusive price (inclusive=True)
    rate          total GST rate in per cent (IGST rate; CGST and SGST are half each)
    inter_state   True -> IGST; False -> CGST + SGST/UTGST
    reverse_charge True -> tax is shown but paid by the recipient, not collected by supplier
    round_total   True -> round the invoice total to the nearest rupee (s.170 style)
    """
    amt = _d(amount)
    if amt < 0:
        raise ValueError("amount must not be negative (use a credit note for reductions)")
    r, warnings = check_rate(rate, strict=strict)

    if inclusive:
        tax_exact = amt * r / (Decimal(100) + r)
        if inter_state:
            igst = to_paise(tax_exact)
            cgst = sgst = Decimal("0.00")
        else:
            cgst = sgst = to_paise(tax_exact / 2)
            igst = Decimal("0.00")
        taxable = to_paise(amt) - cgst - sgst - igst
    else:
        taxable = to_paise(amt)
        if inter_state:
            igst = to_paise(taxable * r / 100)
            cgst = sgst = Decimal("0.00")
        else:
            cgst = sgst = to_paise(taxable * r / 200)
            igst = Decimal("0.00")

    tax = cgst + sgst + igst
    gross = taxable + tax
    payable_to_supplier = taxable if reverse_charge else gross
    round_off = Decimal("0.00")
    if round_total:
        rounded = round_rupee(payable_to_supplier)
        round_off = to_paise(rounded - payable_to_supplier)
        payable_to_supplier = to_paise(rounded)

    return {
        "rate": r,
        "supply_type": "inter-state" if inter_state else "intra-state",
        "taxable_value": taxable,
        "cgst_rate": Decimal(0) if inter_state else r / 2,
        "sgst_rate": Decimal(0) if inter_state else r / 2,
        "igst_rate": r if inter_state else Decimal(0),
        "cgst": cgst,
        "sgst": sgst,
        "igst": igst,
        "total_tax": tax,
        "reverse_charge": reverse_charge,
        "tax_paid_by": "recipient" if reverse_charge else "supplier",
        "round_off": round_off,
        "total": payable_to_supplier,
        "warnings": warnings,
    }


def calculate_invoice(lines, *, inter_state=False, reverse_charge=False,
                      round_total=False, strict=False) -> dict:
    """lines: iterable of dicts with 'amount', 'rate' and optional 'inclusive'.

    Tax is computed and rounded per line, then summed (avoid recomputing on the total).
    """
    results = [calculate(l["amount"], l["rate"], inclusive=l.get("inclusive", False),
                         inter_state=inter_state, reverse_charge=reverse_charge,
                         strict=strict) for l in lines]
    summary = {k: sum((x[k] for x in results), Decimal("0.00"))
               for k in ("taxable_value", "cgst", "sgst", "igst", "total_tax", "total")}
    summary["round_off"] = Decimal("0.00")
    if round_total:
        rounded = round_rupee(summary["total"])
        summary["round_off"] = to_paise(rounded - summary["total"])
        summary["total"] = to_paise(rounded)
    summary["lines"] = results
    summary["reverse_charge"] = reverse_charge
    summary["warnings"] = sorted({w for x in results for w in x["warnings"]})
    return summary


def _jsonable(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_jsonable(v) for v in obj]
    return obj


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="GST calculator (India). Not tax advice.")
    p.add_argument("amount", help="taxable value, or tax-inclusive price with --inclusive")
    p.add_argument("--rate", required=True, help="total GST rate in per cent, e.g. 18")
    p.add_argument("--inclusive", action="store_true", help="amount already includes GST")
    p.add_argument("--inter-state", action="store_true", help="IGST instead of CGST+SGST")
    p.add_argument("--reverse-charge", action="store_true", help="recipient pays the tax")
    p.add_argument("--round-total", action="store_true", help="round total to nearest rupee")
    p.add_argument("--strict", action="store_true", help="reject rates not notified from 22 Sep 2025")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        r = calculate(a.amount, a.rate, inclusive=a.inclusive, inter_state=a.inter_state,
                      reverse_charge=a.reverse_charge, round_total=a.round_total, strict=a.strict)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(_jsonable(r), indent=2, ensure_ascii=False))
        return 0
    print(f"Supply type     : {r['supply_type']}{' (reverse charge)' if r['reverse_charge'] else ''}")
    print(f"Taxable value   : {r['taxable_value']}")
    if a.inter_state:
        print(f"IGST @ {r['igst_rate']}%    : {r['igst']}")
    else:
        print(f"CGST @ {r['cgst_rate']}%    : {r['cgst']}")
        print(f"SGST @ {r['sgst_rate']}%    : {r['sgst']}")
    if r["round_off"]:
        print(f"Round off       : {r['round_off']}")
    print(f"Total {'(payable to supplier)' if r['reverse_charge'] else ''}: {r['total']}")
    if r["reverse_charge"]:
        print(f"Tax payable by recipient under reverse charge: {r['total_tax']}")
    for w in r["warnings"]:
        print(f"warning: {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
