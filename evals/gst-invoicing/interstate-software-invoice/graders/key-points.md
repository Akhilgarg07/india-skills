---
type: llm
---

PASS only if the response does ALL of the following:
1. Charges IGST at 18% only, with no CGST/SGST, because the supplier (Karnataka) and the place of supply (Maharashtra) are in different states.
2. Shows the place of supply as Maharashtra with state code 27, and the supplier and recipient GSTINs.
3. Uses a SAC code for IT/software services (e.g. 998313 or 998314, under heading 9983) rather than a goods HSN code.
4. States or asks whether ₹1,18,000 includes GST. If treated as inclusive, the taxable value is ₹1,00,000 and IGST ₹18,000. If exclusive, IGST is ₹21,240 and the total ₹1,39,240.
5. Includes the other mandatory particulars: an invoice number (max 16 characters, unique per financial year), invoice date, a reverse charge Yes/No indication, and a note that an IRN/QR code is needed if the supplier's turnover exceeds ₹5 crore (e-invoicing).

FAIL if the invoice charges CGST + SGST, or omits the place of supply.
