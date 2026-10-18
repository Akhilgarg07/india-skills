---
type: llm
---

PASS only if the response does ALL of the following:
1. Says CGST and SGST should each be computed from the taxable value at half the rate, so they are always equal (not total minus the other half).
2. Recommends per-line computation and rounding to paise (half-up), then summing lines.
3. Recommends decimal/integer-paise arithmetic instead of floats.
4. Mentions that any rounding of the invoice total to rupees goes on a separate round-off line (and/or cites section 170 nearest-rupee rounding with 50 paise rounding up).

FAIL if the answer keeps the 'sgst = tax - cgst' approach.
