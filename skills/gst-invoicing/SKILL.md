---
name: gst-invoicing
description: Generate and validate Indian GST tax invoices - mandatory Rule 46 fields, invoice numbering (max 16 chars, unique per financial year), CGST+SGST/UTGST vs IGST based on supplier state vs place of supply, HSN/SAC digit rules, place-of-supply basics for goods and services, B2C vs B2B details, export/SEZ endorsements, and e-invoicing (IRN/QR) thresholds. Use when building invoice generators, billing/ERP or e-commerce checkout code, invoice PDF templates, GSTR-1 exports, or when asked to create or review a GST invoice. Includes a stdlib invoice checker.
license: MIT
metadata:
  version: "0.1.0"
  last-verified: "2026-10-18"
---

# GST invoicing

> **Not tax advice.** Invoice rules come from the CGST Act, CGST Rules and CBIC/GSTN
> notifications, which change with GST Council meetings and Union Budgets. Confirm the
> current rules (and the rate for each HSN/SAC) before going live.

For computing tax amounts and rounding, also use the `gst-tax-calculation` skill.

## Workflow for "generate a GST invoice"

1. **Collect or confirm the inputs.** Supplier GSTIN and state; recipient GSTIN (or that
   they are unregistered) and address; place of supply; goods or services; HSN/SAC;
   **whether the amount is tax-exclusive or tax-inclusive** (ask if unclear; ₹1,18,000 at
   18% inclusive means taxable value ₹1,00,000).
2. **Decide intra- vs inter-state:** supplier's state vs **place of supply**
   (not the recipient's billing state by default; see below).
   - Same state/UT → **CGST + SGST** (or **UTGST** in Chandigarh, Lakshadweep, Andaman &
     Nicobar, Dadra & Nagar Haveli and Daman & Diu, and other UTs without legislature).
   - Different states, exports, or **any supply to/by an SEZ unit or developer** → **IGST**.
3. **Fill every Rule 46 field** (table below) and compute tax per line.
4. **e-invoicing:** if the supplier's aggregate turnover in any FY since 2017-18 exceeds
   **₹5 crore**, B2B, export and SEZ invoices must be reported to an IRP to get an
   **IRN + signed QR code**. Without them the document is not a valid invoice.
5. Validate with `scripts/invoice_check.py`.

Worked example (Karnataka → Maharashtra, registered recipient, software services):
SAC `998314` (IT design and development services), place of supply = recipient's location
(Maharashtra, 27) → **inter-state → IGST 18%**. If ₹1,18,000 is the inclusive price:
taxable value ₹1,00,000, IGST ₹18,000, total ₹1,18,000. No CGST/SGST lines.

## Mandatory particulars (CGST Rule 46)

| # | Field | Notes |
|---|---|---|
| a | Supplier name, address, GSTIN | |
| b | Invoice number | Consecutive, ≤ **16 characters**, letters/digits/`-`/`/` only, **unique per financial year**; multiple series allowed |
| c | Date of issue | |
| d | Recipient name, address, GSTIN/UIN | if registered |
| e | Unregistered recipient: name, address, delivery address, **state name and code** | mandatory if taxable value ≥ **₹50,000**; below that only if the recipient asks (f) |
| g | HSN (goods) / SAC (services) code | digits per turnover; see below |
| h | Description | |
| i | Quantity and unit (UQC) | goods |
| j-k | Total value; taxable value after discount/abatement | |
| l-m | Rate and amount of CGST/SGST/UTGST/IGST/cess | per line |
| n | **Place of supply with state name** | for inter-state supplies (show it always; it's the basis of the tax type) |
| o | Delivery address if different from place of supply | |
| p | **Whether tax is payable on reverse charge** | "Reverse charge: Yes/No" |
| q | Signature or digital signature | not required on an electronic invoice under the IT Act |
| r | QR code with embedded IRN | when issued under e-invoicing (rule 48(4)) |

Full text, export/SEZ endorsements, copies (ORIGINAL FOR RECIPIENT, etc.) and time
limits: [references/mandatory-fields.md](references/mandatory-fields.md).

**HSN/SAC digits** (Notification 78/2020-CT, from 1 Apr 2021): aggregate turnover in
previous FY **up to ₹5 crore → 4 digits** (B2C invoices may omit HSN); **above ₹5 crore → 6 digits**
(8 digits also fine). Services codes start with `99` (e.g. 998314).

## Place of supply: general rules (IGST Act)

- **Goods with movement:** where the movement **terminates** for delivery (s.10(1)(a)).
  "Bill-to/ship-to" on a third party's direction: the third party's principal place of business (s.10(1)(b)).
- **Goods to an unregistered person** (from 1 Oct 2023): the address recorded on the
  invoice (state name counts); if none, the supplier's location (s.10(1)(ca)). E-commerce
  sellers should record the **delivery** state.
- **Services, general rule (s.12(2)):** registered recipient → recipient's location;
  unregistered → recipient's address on record, else the supplier's location.
- **Exceptions are common**: immovable property, hotels and events (property location),
  restaurant, beauty and fitness (where performed), passenger and goods transport, events,
  telecom, banking, insurance. Exports/imports follow s.13. See
  [references/place-of-supply.md](references/place-of-supply.md).

## e-invoicing (IRN)

- Applies if aggregate turnover in **any** FY from 2017-18 onwards **exceeded ₹5 crore**
  (from 1 Aug 2023, Notification 10/2023-CT). It covers B2B invoices, credit/debit notes,
  exports and SEZ supplies. B2C invoices are not e-invoiced (large taxpayers instead put a
  dynamic QR on B2C invoices; see references).
- **30-day limit:** taxpayers with AATO **≥ ₹10 crore** cannot report invoices/notes older than
  **30 days** to the IRP (from 1 Apr 2025).
- **Exempt suppliers:** SEZ units, insurers, banks, financial institutions and NBFCs, GTAs,
  passenger transport, multiplex cinema admission, Government departments and local authorities.
- Flow: build INV-01 JSON → IRP validates and returns **IRN** (hash), **Ack No/Date** and
  **signed QR** → print the QR on the invoice. Cancellation is possible only within 24 hours
  on the IRP. After that, issue a credit note. Details: [references/e-invoicing.md](references/e-invoicing.md).

## Rules for invoice code

- Never derive IGST vs CGST/SGST from the **customer's GSTIN state alone** for goods; the
  place of supply (delivery) decides. For B2B services the recipient's registered location
  usually decides.
- Never issue an invoice with both IGST and CGST/SGST on the same line.
- Invoice number generator: per-FY sequence (`INV/2026-27/0042` = 16 chars), no gaps reused,
  no special characters other than `-` and `/`, no spaces.
- Store state as the 2-digit GST code plus name. Use code `96` (Other Country) for exports
  in e-invoice JSON.
- Corrections after issue: **credit note / debit note** referencing the original invoice,
  not edits to an issued invoice.
- B2C below ₹50,000 with an unregistered buyer may omit buyer details, but recording the
  state is still needed to determine the place of supply for inter-state B2C.

## Script

```bash
python3 scripts/invoice_check.py --example > sample.json   # a correct inter-state B2B invoice
python3 scripts/invoice_check.py invoice.json              # errors + warnings, exit 1 on error
```
Module: `check_invoice(dict)`, `supply_type(supplier_state, pos, sez=, export=)`,
`general_place_of_supply(kind, recipient_registered=, ...)`. `scripts/gstin_validate.py` is a
copy of the one in `indian-id-validation`.

Sources and verification dates: [references/sources.md](references/sources.md).
