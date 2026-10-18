---
description: Paise rounding and CGST/SGST split in an invoice generator.
tags: [gst-tax-calculation, rounding]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  Use decimal arithmetic, compute per line, compute CGST and SGST each from taxable
  value at half rate (equal), round half-up to paise, show a separate round-off line;
  s.170 rounds amounts payable to nearest rupee.
---

In our Node.js invoice generator we compute `const tax = Math.round(total * 0.18 * 100) / 100; const cgst = Math.round(tax / 2 * 100) / 100; const sgst = tax - cgst;` on the invoice total. Customers sometimes see CGST ₹7.71 and SGST ₹7.70. How should GST rounding work?
