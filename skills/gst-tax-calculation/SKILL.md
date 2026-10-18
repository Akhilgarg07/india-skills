---
name: gst-tax-calculation
description: Calculate Indian GST correctly - current rate slabs (5% / 18% / 40% plus 0%, 0.25%, 1.5% and 3% since 22 Sep 2025), CGST+SGST vs IGST split, tax-exclusive vs tax-inclusive (MRP) back-calculation, paise and rupee rounding (section 170 CGST Act), and reverse charge basics. Use when writing or reviewing pricing, cart, checkout, billing or accounting code that computes GST, when someone asks "how much GST on X", or when code still uses the old 12% / 28% slabs. Includes a stdlib Decimal-based Python calculator.
license: MIT
metadata:
  version: "0.1.0"
  last-verified: "2026-10-18"
---

# GST tax calculation

> **Not tax advice.** GST rates are set by GST Council recommendations and
> notifications, and the rules around them change with GST Council meetings and each
> Union Budget. Always confirm the rate for the specific HSN/SAC code in the current
> rate notification before shipping.

## Current rate structure (from 22 September 2025)

The 56th GST Council meeting replaced the four slabs (5/12/18/28%) with:

| Total GST | CGST + SGST (intra-state) | IGST (inter-state) | Used for |
|---|---|---|---|
| 0% | nil / exempt | nil / exempt | notified essentials, exempt services |
| 5% | 2.5% + 2.5% | 5% | "merit rate" |
| 18% | 9% + 9% | 18% | "standard rate" (default for most goods and services) |
| 40% | 20% + 20% | 40% | "special/de-merit rate": select sin and luxury goods |
| 3%, 1.5%, 0.25% | half each | full | special schedules (precious metals/stones etc.) |

- **12% and 28% are gone** for almost all supplies since 22 Sep 2025. Tobacco/pan masala
  stayed on 28% + compensation cess until **31 Jan 2026**; from **1 Feb 2026** they moved to
  40% (bidi to 18%) and the compensation cess on them ended.
- Code that hard-codes `[5, 12, 18, 28]` is out of date. Rates belong in **data keyed by
  HSN/SAC and effective date**, not in code constants.
- The **rate depends on the item (HSN/SAC) and the date of supply**, never on the price
  alone (a few entries do have price conditions, e.g. hotel room tariffs; read the entry).
- Full schedule list and history: [references/rate-slabs.md](references/rate-slabs.md).

## Core formulas

Let `r` = total GST rate in per cent, `V` = taxable value (price before GST).

```
Tax-exclusive:  tax = V × r / 100                       total = V + tax
Tax-inclusive:  tax = P × r / (100 + r)                 V = P − tax
Intra-state:    CGST = SGST (or UTGST) = V × (r/2) / 100
Inter-state:    IGST = V × r / 100
```

Worked: ₹1,18,000 inclusive at 18% → V = 1,18,000 × 100/118 = ₹1,00,000; tax ₹18,000
(intra: CGST ₹9,000 + SGST ₹9,000; inter: IGST ₹18,000).
**Wrong:** 1,18,000 × 18% = 21,240. Never apply the rate to an inclusive price.

Intra- vs inter-state depends on **supplier location vs place of supply**, not on where
the customer's billing address or the buyer's GSTIN state is in every case. See the
`gst-invoicing` skill for place-of-supply basics.

## Rounding

- **Use decimal arithmetic** (`decimal.Decimal`, `BigDecimal`, `decimal.js`, integer paise).
  Never binary floats.
- Compute tax **per line item**, round each tax component (CGST, SGST, IGST) to paise
  (half-up), then sum lines. Compute CGST and SGST separately with the same half-rate so
  they are always equal; don't compute total tax and split the remainder unevenly.
- **Section 170 CGST Act:** tax, interest, penalty, refunds etc. payable under the Act
  are rounded to the nearest rupee: 50 paise or more goes up, less than 50 paise is ignored.
  This governs amounts paid/returned. Invoices may show paise. If you round the invoice
  total to rupees, show the difference as a separate "Round off" line; never fold it
  into the tax.
- For inclusive prices, derive tax from the price and set `V = P − tax` so
  `V + tax == P` exactly.
- Details and edge cases: [references/rounding.md](references/rounding.md).

## Reverse charge (RCM) basics

- Normally the supplier collects GST. Under **reverse charge** the **recipient** pays it.
- **Section 9(3) CGST Act / 5(3) IGST Act:** notified categories of supply. Examples from the
  notified list: goods transport agency (GTA) services to factories, companies, firms and
  registered persons; legal services by an advocate to a business entity; services by an
  arbitral tribunal; sponsorship to a body corporate or firm; services by a director to
  the company; services by insurance agents to insurers; recovery agents to banks/NBFCs;
  most services by Government to business entities; import of services.
- **Section 9(4):** only for a **class of registered persons notified** by the Government
  for specified supplies from **unregistered** suppliers (not a general rule since 2019).
- **Effects on code:**
  - The supplier's invoice must say tax is payable on reverse charge, and the supplier
    does **not** collect the GST amount. The recipient pays the tax.
  - The recipient pays RCM tax **in cash** (electronic cash ledger), not from input tax
    credit. It can then claim ITC if otherwise eligible.
  - A recipient liable under RCM must register regardless of the turnover threshold.
- The RCM list is amended often (e.g. renting of commercial property by an unregistered person
  to a registered person was put under RCM from 10 Oct 2024 and moved back to forward
  charge by notification 07/2025-CT(Rate) dated 16 Jan 2025). See
  [references/reverse-charge.md](references/reverse-charge.md).

## Script

```bash
python3 scripts/gst_calc.py 100000 --rate 18                        # CGST 9,000 + SGST 9,000
python3 scripts/gst_calc.py 118000 --rate 18 --inclusive --inter-state  # back-calc, IGST
python3 scripts/gst_calc.py 5000 --rate 18 --reverse-charge          # supplier collects 5,000
python3 scripts/gst_calc.py 999.99 --rate 5 --round-total --json
```

As a module: `calculate(amount, rate, inclusive=, inter_state=, reverse_charge=,
round_total=, strict=)` and `calculate_invoice(lines, ...)` return Decimal fields;
`round_rupee()` implements section 170. Non-current rates (e.g. 12, 28) produce a
warning, or an error with `strict=True`.

## Checklist for GST code

- [ ] Rates come from a table keyed by HSN/SAC + effective date; old invoices keep old rates.
- [ ] Decimal money; per-line rounding to paise; CGST == SGST; separate round-off line.
- [ ] Intra/inter decided from supplier state vs place of supply.
- [ ] Inclusive prices back-calculated with `r/(100+r)`.
- [ ] A discount reduces the taxable value only if it is given before or at the time of
      supply and recorded on the invoice, or (post-supply) was agreed before the supply and
      is linked to specific invoices (s.15(3)). Post-supply reductions and returns go on a
      credit note, never a negative invoice.
- [ ] Reverse-charge invoices flagged, and tax not collected from the customer.
- [ ] The rate change effective date is handled (invoices around 22 Sep 2025 follow the
      time-of-supply rules in section 14 CGST Act).

Sources and verification dates: [references/sources.md](references/sources.md).
