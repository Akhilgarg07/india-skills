---
type: llm
---

PASS only if the response does ALL of the following:
1. Uses Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }) (or toLocaleString('en-IN', ...)) to produce ₹12,34,567, and explains the last-three-then-twos grouping.
2. Warns that notation:'compact' rounds by default (e.g. 13L) and/or that compactDisplay:'long' outputs 'million', so a custom formatter or explicit fraction digits is needed for '12.35 lakh' / '2.5 crore'.
3. Provides a lakh/crore short-form implementation dividing by 1,00,000 and 1,00,00,000 with explicit rounding.
4. Mentions always passing the locale explicitly (not relying on the default locale) or the ICU-data caveat on some runtimes.

FAIL if the answer only uses notation:'compact' without noting the rounding/'million' pitfalls.
