---
description: Contractor payments that cross the aggregate threshold mid-year.
tags: [tds-basics, 194c, threshold]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  No: the aggregate threshold of ₹1,00,000 per FY applies; once crossed (5th payment),
  deduct 2% (firm) on the whole aggregate including earlier untaxed payments; track per-
  payee per-FY aggregates.
---

Our AP system pays a housekeeping contractor (a partnership firm) ₹25,000 every month. We never deduct TDS because each bill is under ₹30,000. Is that right? What should the code do?
