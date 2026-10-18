# e-invoicing (IRN) reference

> Not tax advice. Thresholds and exemptions are set by CBIC notifications (13/2020-CT as
> amended) and change; check the IRP/GST portal advisories.

## Who must e-invoice
- Registered persons whose **aggregate turnover in any financial year from 2017-18 onwards
  exceeds ₹5 crore**, from **1 Aug 2023** (Notification 10/2023-CT).
- Earlier phases: > ₹500 cr (1 Oct 2020), > ₹100 cr (1 Jan 2021), > ₹50 cr (1 Apr 2021),
  > ₹20 cr (1 Apr 2022), > ₹10 cr (1 Oct 2022).
- Once applicable, it stays applicable even if turnover later falls.

## Exempt categories (Notification 13/2020-CT and later amendments)
SEZ units (61/2020-CT); insurers; banking companies; financial institutions; NBFCs; goods
transport agencies (road); suppliers of passenger transportation services; admission to
cinema in multiplex screens; Government departments and local authorities (23/2021-CT).
Exempt taxpayers wrongly shown as enabled can file a declaration on the e-invoice portal.

## Documents and transactions covered
- Tax invoices, **credit notes** and **debit notes**
- B2B supplies, supplies to SEZ (with or without payment), exports (with or without
  payment) and deemed exports
- **Not** B2C. Large taxpayers (> ₹500 cr) put a Dynamic QR on B2C invoices instead.
- 57th GST Council (8 Oct 2026) **recommended** extending e-invoicing to RCM supplies received
  from unregistered persons and to import of services for AATO ≥ ₹5 crore. This is not yet in
  force; watch for the notification.

## Flow
1. ERP builds the INV-01 JSON (seller, buyer, POS, line items with HSN, values, tax).
2. Upload to an **IRP** (Invoice Registration Portal) through API, GSP or web.
3. IRP validates, generates the **IRN** (unique for the supplier GSTIN, financial year,
   document type and document number), signs the invoice, and returns **IRN, Ack No, Ack Date and a signed QR code**.
4. Print the QR (and IRN) on the invoice. Data flows to GSTR-1 and the e-way bill system.

## Time and cancellation rules
- **30-day reporting limit** for AATO **≥ ₹10 crore** (from 1 Apr 2025): the IRP refuses IRNs
  for invoices/notes older than 30 days from the document date. (It applied to AATO ≥ ₹100 cr before.)
- **Cancellation:** an IRN can be cancelled on the IRP only within **24 hours** of generation.
  After that, issue a credit note (or amend in GSTR-1 as the portal allows). Never reuse the
  same invoice number for a new IRN.
- Duplicate IRN requests for the same document number are rejected. Design idempotent retries
  that look up the existing IRN.

## Export-specific JSON rules (IRP validations)
- Recipient GSTIN `URP`, recipient state `96` (Other Country), PIN `999999`, POS `96`.
- Exports and SEZ supplies are always inter-state, so IGST applies.

## Implementation tips
- Keep invoice numbers ≤ 16 characters and unique per FY *per GSTIN*. The IRN hash depends on them.
- Validate GSTINs, HSN digits, state/PIN consistency and tax arithmetic **before** calling the IRP.
- Store IRN, Ack No/Date, signed invoice and signed QR immutably with the invoice.
