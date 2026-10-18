#!/usr/bin/env python3
"""TDS calculator for the two non-salary payments developers meet most often:
payments to contractors and fees for professional / technical services. Also gives
the section to quote under the Income-tax Act 1961 (old) or 2025 (new).

Rules encoded (resident payees; see references/sources.md):
  contractor (old s.194C / new s.393(1) Table Sl. No. 6(i)):
      1% if payee is an individual or HUF, else 2%;
      deduct if a single payment > Rs 30,000 or the year's aggregate > Rs 1,00,000.
  professional / technical fees (old s.194J / new s.393(1) Table Sl. No. 6(iii)):
      2% for fees for technical services (not professional), royalty for sale/
      distribution/exhibition of films, and payees only running a call centre; 10% otherwise;
      deduct once the year's aggregate exceeds Rs 50,000 (Rs 30,000 before 1 Apr 2025).
  no PAN (old s.206AA / new s.397(2)): rate = higher of the rate above and 20%.
  GST shown separately on the invoice is excluded from the TDS base (CBDT Circular 23/2017).
  Which Act: the earlier of credit or payment; on/after 1 Apr 2026 -> Income-tax Act 2025.
The Act changed section numbers, not rates or thresholds (CBDT/e-filing portal FAQ).

Module usage:
    >>> from tds_calc import compute
    >>> r = compute("professional", "100000", payee_type="individual", event_date="2026-06-15")
    >>> str(r["tds"]), r["section"]
    ('10000.00', 'Income-tax Act 2025, s.393(1) [Table: Sl. No. 6(iii)]')

CLI usage:
    python3 tds_calc.py contractor 45000 --payee individual --date 2026-07-01
    python3 tds_calc.py professional 60000 --no-pan --date 2026-05-10
    python3 tds_calc.py technical 80000 --gst 14400 --date 2026-05-10 --json

Salary TDS (old s.192 / new s.392) depends on the employee's projected income, regime and
slabs; it is out of scope for this calculator (see SKILL.md).

Standard library only. Not tax advice.
"""

import argparse
import datetime as dt
import json
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

NEW_ACT_FROM = dt.date(2026, 4, 1)
J_THRESHOLD_RAISED = dt.date(2025, 4, 1)
NO_PAN_RATE = Decimal("20")
INDIVIDUAL_LIKE = {"individual", "huf"}

SECTIONS = {
    "contractor": ("s.194C", "s.393(1) [Table: Sl. No. 6(i)]"),
    "professional": ("s.194J", "s.393(1) [Table: Sl. No. 6(iii)]"),
    "technical": ("s.194J", "s.393(1) [Table: Sl. No. 6(iii)]"),
    "call_centre": ("s.194J", "s.393(1) [Table: Sl. No. 6(iii)]"),
    "film_royalty": ("s.194J", "s.393(1) [Table: Sl. No. 6(iii)]"),
}
NO_PAN_SECTION = ("s.206AA", "s.397(2)")


def _d(v, what):
    try:
        d = Decimal(str(v).replace(",", "").replace("₹", "").strip())
    except InvalidOperation:
        raise ValueError(f"{what} {v!r} is not a number") from None
    if not d.is_finite() or d < 0:
        raise ValueError(f"{what} must be a non-negative number")
    return d


def _date(v):
    if v is None:
        return dt.date.today()
    if isinstance(v, dt.date):
        return v
    return dt.date.fromisoformat(str(v))


def governing_act(event_date) -> str:
    """Earlier of credit or payment decides: before 1 Apr 2026 -> 1961 Act."""
    return "Income-tax Act 2025" if _date(event_date) >= NEW_ACT_FROM else "Income-tax Act 1961"


def section_for(payment_type: str, event_date=None, *, pan=True) -> str:
    if payment_type not in SECTIONS:
        raise ValueError(f"payment_type must be one of {sorted(SECTIONS)}")
    new = _date(event_date) >= NEW_ACT_FROM
    s = SECTIONS[payment_type][1 if new else 0]
    act = governing_act(event_date)
    text = f"{act}, {s}"
    if not pan:
        text += f" read with {NO_PAN_SECTION[1 if new else 0]}"
    return text


def base_rate(payment_type: str, payee_type: str) -> Decimal:
    if payment_type == "contractor":
        return Decimal("1") if payee_type in INDIVIDUAL_LIKE else Decimal("2")
    if payment_type in ("technical", "call_centre", "film_royalty"):
        return Decimal("2")
    if payment_type == "professional":
        return Decimal("10")
    raise ValueError(f"payment_type must be one of {sorted(SECTIONS)}")


def compute(payment_type, amount, *, payee_type="company", pan=True, gst="0",
            paid_earlier_in_year="0", tds_base_earlier_in_year="0", event_date=None) -> dict:
    """TDS on one payment/credit to a resident.

    amount                   invoice amount (incl. GST if gst > 0)
    gst                      GST shown separately on the invoice (excluded from the base)
    paid_earlier_in_year     total of earlier amounts (excl. GST) to this payee, same FY,
                             same payment type
    tds_base_earlier_in_year part of those earlier amounts on which TDS was already deducted
    """
    when = _date(event_date)
    amt, gst_amt = _d(amount, "amount"), _d(gst, "gst")
    if gst_amt > amt:
        raise ValueError("gst cannot exceed amount")
    earlier, earlier_taxed = _d(paid_earlier_in_year, "paid_earlier_in_year"), _d(
        tds_base_earlier_in_year, "tds_base_earlier_in_year")
    if earlier_taxed > earlier:
        raise ValueError("tds_base_earlier_in_year cannot exceed paid_earlier_in_year")

    this_base = amt - gst_amt
    aggregate = earlier + this_base
    untaxed_earlier = earlier - earlier_taxed
    notes = []
    if gst_amt:
        notes.append("GST shown separately excluded from the TDS base (CBDT Circular 23/2017)")

    if payment_type == "contractor":
        single, agg_limit = Decimal("30000"), Decimal("100000")
        if aggregate > agg_limit:
            base = this_base + untaxed_earlier
            if untaxed_earlier:
                notes.append("aggregate crossed Rs 1,00,000: TDS also covers earlier untaxed payments")
        elif this_base > single:
            base = this_base
        else:
            base = Decimal(0)
            notes.append("below thresholds (single payment <= Rs 30,000 and aggregate <= Rs 1,00,000)")
    else:
        limit = Decimal("50000") if when >= J_THRESHOLD_RAISED else Decimal("30000")
        if aggregate > limit:
            base = this_base + untaxed_earlier
            if untaxed_earlier:
                notes.append(f"aggregate crossed Rs {limit:,}: TDS also covers earlier untaxed fees")
        else:
            base = Decimal(0)
            notes.append(f"aggregate for the year does not exceed Rs {limit:,}")

    rate = base_rate(payment_type, payee_type)
    if not pan:
        rate = max(rate, NO_PAN_RATE)
        notes.append("no PAN: higher of the normal rate and 20%")
    tds = (base * rate / 100).quantize(Decimal("0.01"), ROUND_HALF_UP)

    return {
        "payment_type": payment_type,
        "act": governing_act(when),
        "section": section_for(payment_type, when, pan=pan),
        "rate": rate,
        "tds_base": base,
        "tds": tds,
        "net_payable": amt - tds,
        "notes": notes,
    }


def _jsonable(o):
    return {k: (str(v) if isinstance(v, Decimal) else v) for k, v in o.items()}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="TDS on contractor / professional fees (India). Not tax advice.")
    p.add_argument("payment_type", choices=sorted(SECTIONS))
    p.add_argument("amount")
    p.add_argument("--payee", default="company",
                   help="individual, huf, company, firm, ... (contractor rate depends on it)")
    p.add_argument("--no-pan", action="store_true")
    p.add_argument("--gst", default="0", help="GST shown separately on the invoice")
    p.add_argument("--earlier", default="0", help="earlier amounts to this payee this FY")
    p.add_argument("--earlier-taxed", default="0", help="part of --earlier already subjected to TDS")
    p.add_argument("--date", default=None, help="earlier of credit/payment date, YYYY-MM-DD")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        r = compute(a.payment_type, a.amount, payee_type=a.payee, pan=not a.no_pan, gst=a.gst,
                    paid_earlier_in_year=a.earlier, tds_base_earlier_in_year=a.earlier_taxed,
                    event_date=a.date)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(_jsonable(r), indent=2, ensure_ascii=False))
        return 0
    print(f"Section     : {r['section']}")
    print(f"Rate        : {r['rate']}%")
    print(f"TDS base    : {r['tds_base']}")
    print(f"TDS         : {r['tds']}")
    print(f"Net payable : {r['net_payable']}")
    for n in r["notes"]:
        print(f"note: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
