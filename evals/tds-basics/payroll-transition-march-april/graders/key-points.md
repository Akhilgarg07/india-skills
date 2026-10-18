---
type: llm
---

PASS only if the response does ALL of the following:
1. Says March 2026 salary paid on 31 March 2026 is governed by section 192 of the Income-tax Act 1961, and April 2026 salary by section 392(1) of the Income-tax Act 2025 (salary TDS follows the payment date).
2. Says the employer must reset the TDS computation from 1 April 2026 for Tax Year 2026-27 (projected income, deductions, regime).
3. Mentions updating section numbering/terminology in the system, e.g. investment declarations now reference the new Act (80C → Schedule XV read with section 123) and 'tax year' replaces 'previous year/assessment year'.
4. Notes that rates/thresholds were retained (it is a renumbering, not a policy change) or that slab rates must come from versioned configuration.

FAIL if the answer says the new Act section applies to the March 2026 salary, or ignores the Income-tax Act 2025.
