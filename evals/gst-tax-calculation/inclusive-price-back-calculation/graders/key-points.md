---
type: llm
---

PASS only if the response does ALL of the following:
1. Computes the taxable value as ₹1,00,000 and the GST as ₹18,000, using price × r/(100+r) or price ÷ 1.18.
2. Explains that price × 0.18 (₹21,240) is wrong because it applies the rate to a price that already includes tax.
3. Identifies the tax as IGST (inter-state), not CGST+SGST.
4. Recommends decimal or integer-paise arithmetic rather than binary floating point.

FAIL if the answer states GST of ₹21,240 or a taxable value other than ₹1,00,000.
