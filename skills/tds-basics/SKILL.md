---
name: tds-basics
description: Indian TDS (tax deducted at source) basics for developers - salary, payments to contractors and fees for professional/technical services; rates, thresholds, the no-PAN 20% rule, GST exclusion, and the switch from the Income-tax Act 1961 (sections 192/194C/194J/206AA) to the Income-tax Act 2025 (sections 392/393/397, "tax year") from 1 April 2026. Use when building payroll, vendor-payment, accounts-payable, freelancer/marketplace payout or invoicing code that withholds tax, when generating TDS entries or returns, or when someone asks how much TDS to deduct. Includes a stdlib Python TDS calculator.
license: MIT
metadata:
  version: "0.1.0"
  last-verified: "2026-10-18"
---

# TDS basics

> **Not tax advice.** TDS rates, thresholds and section numbers change with each Union
> Budget (Finance Act) and the Income-tax Rules. Confirm current rules, or have a tax
> professional review, before relying on any figure.

## First: which Act? (big change on 1 April 2026)

- The **Income-tax Act, 2025** replaced the 1961 Act **from 1 April 2026**. "Previous year"
  and "assessment year" are replaced by **tax year** (FY 2026-27 = Tax Year 2026-27).
- All TDS sections 192-194T of the old Act are consolidated into **section 392 (salary)** and
  **section 393 (tables of all other payments)**. **Rates and thresholds were retained.** Only
  the numbering and terminology changed.
- **Trigger:** the **earlier of credit (in books) or payment**. If it is on or before 31 Mar
  2026, the old Act applies (and old forms and returns, even when filed later). If it is on
  or after 1 Apr 2026, the new Act applies. Salary follows the **payment date**.
- Quoting an old section (e.g. `194C`) for a post-April-2026 payment causes TDS return
  processing errors. **Update ERP/payroll section codes.**

| Payment | Old Act (≤ 31 Mar 2026) | New Act (≥ 1 Apr 2026) |
|---|---|---|
| Salary | s.192 | s.392(1) |
| Contractor / sub-contractor | s.194C | s.393(1) [Table: Sl. No. 6(i)] |
| Fees for professional / technical services | s.194J | s.393(1) [Table: Sl. No. 6(iii)] |
| No PAN (higher rate) | s.206AA | s.397(2) |
| Purchase of goods (buyer) / e-commerce operator | s.194Q / s.194-O | s.393(1) [Table: Sl. No. 8(ii) / 8(v)] |

More mappings and details: [references/sections.md](references/sections.md).

## Rates and thresholds (resident payees)

| Payment | Rate | Deduct when |
|---|---|---|
| Contractor: payee is an individual or HUF | **1%** | single payment > ₹30,000 **or** aggregate in the year > ₹1,00,000 |
| Contractor: any other payee (company, firm, LLP...) | **2%** | same |
| Fees for **technical** services (not professional), payee only runs a call centre, royalty for film sale/distribution/exhibition | **2%** | aggregate in the year > ₹50,000 |
| Fees for **professional** services and other covered sums | **10%** | aggregate in the year > ₹50,000 (₹30,000 before 1 Apr 2025) |
| Salary | average rate on estimated annual salary income | when tax is payable on estimated income |

- Once an aggregate threshold is crossed, deduct on the **whole** amount paid/credited in
  the year (including earlier untaxed payments), not just the excess.
- **Individuals/HUFs** as payers deduct under the contractor/professional provisions only if
  their turnover/receipts in the previous year exceeded ₹1 crore (business) / ₹50 lakh
  (profession). Other individuals use a separate provision (old s.194M).
- **GST:** if the GST component is shown separately on the invoice, deduct TDS on the amount
  **excluding GST** (CBDT Circular 23/2017; old-Act circulars continue under the new Act unless
  inconsistent).
- **Contractor vs professional:** "work" (including supply of labour, advertising,
  broadcasting and telecasting, carriage of goods or passengers other than by rail, and
  catering) is a contractor payment. "Professional services" means legal, medical, engineering,
  architectural, accountancy, technical consultancy, interior decoration, advertising and other
  notified professions. CBDT Circular 5/2002 examples: paying a media house for ad space →
  contractor; an ad agency paying models/artists → professional; routine maintenance with spares →
  contractor, but technical services → professional/technical fees; recruitment agency fees →
  professional/technical fees. Decide by the nature of the payment, not the vendor's title.

## No PAN

If the payee doesn't furnish a valid PAN: deduct at the **higher of the normal rate and 20%**
(5% instead of 20% for the buyer/e-commerce operator provisions). The old "non-filer" higher rate
(s.206AB) was **omitted from 1 Apr 2025**; don't implement it for new payments.
Validate PAN format with the `indian-id-validation` skill. A format-valid PAN is still not a
verified PAN.

## Salary (s.192 / s.392)

- The employer estimates the employee's **annual** taxable salary for the tax year, computes
  tax under the employee's **chosen regime** (the new regime is the default if the employee
  doesn't intimate otherwise), subtracts tax already deducted, and spreads the balance over the
  remaining months (**average rate**). Recompute when salary, declarations or the regime change.
- From 1 Apr 2026 the employer resets the computation for Tax Year 2026-27. Investment
  declarations reference the new Act (e.g. old s.80C → Schedule XV read with s.123).
- Slab rates, rebate and standard deduction change in Finance Acts. Read them from config with
  an effective year; never hard-code them in payroll logic.
- `TODO(verify):` how the no-PAN 20% rule interacts with salary TDS under s.392.

## Deposit, returns and consequences

- Deposit TDS by the 7th of the next month; **March deductions by 30 April**.
- Late deduction: interest **1% per month**. Deducted but deposited late: **1.5% per month**.
- Not deducting can make the payer an "assessee in default" and **disallows 30%** of the
  expense in computing business income (old s.40(a)(ia) → new s.35(b)).
- Quarterly TDS statements and certificates: keep old-Act forms for periods up to Mar 2026;
  new-Act formats from Apr 2026 (Income-tax Rules 2026, e.g. common challan-cum-statement Form 141
  replacing 26QB/QC/QD/QE).

## Script

```bash
python3 scripts/tds_calc.py contractor 45000 --payee individual --date 2026-07-01   # 1% = 450
python3 scripts/tds_calc.py professional 60000 --no-pan --date 2026-05-10          # 20% = 12,000
python3 scripts/tds_calc.py technical 80000 --gst 14400 --date 2026-05-10          # base 65,600
python3 scripts/tds_calc.py contractor 20000 --earlier 90000 --date 2026-01-10     # catch-up
```
Module: `compute(payment_type, amount, payee_type=, pan=, gst=, paid_earlier_in_year=,
tds_base_earlier_in_year=, event_date=)`, `section_for(type, date)`, `governing_act(date)`.
It covers resident payees only. Non-resident payments (old s.195 / new s.393(2)) need a
professional.

## Design rules for TDS code

- Key every rule by **payment type + payee type + event date** (credit or payment, whichever is
  earlier). Keep rates and thresholds in versioned config.
- Track **per payee, per FY, per payment type** aggregates for thresholds.
- Store PAN status at the time of deduction; the rate depends on it.
- Use decimal money; keep TDS base, rate, amount and section code on each payment record for
  the quarterly statement.

Sources and verification dates: [references/sources.md](references/sources.md).
