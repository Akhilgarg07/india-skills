---
description: Showing revenue in lakh/crore in a React dashboard.
tags: [indian-number-formatting, intl]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  Intl.NumberFormat('en-IN', {style:'currency', currency:'INR'}); explains 3-then-2
  grouping; compact notation pitfalls (rounding, long display gives million); custom
  lakh/crore short form; pass locale explicitly; ICU caveat.
---

Our React dashboard shows revenue like ₹1,234,567 and 1.3M. Indian users want ₹12,34,567 and '12.35 lakh' / '2.5 crore'. What's the right way?
