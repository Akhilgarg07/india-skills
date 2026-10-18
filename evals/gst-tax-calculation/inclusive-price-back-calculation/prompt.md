---
description: Back-calculating GST from a tax-inclusive price.
tags: [gst-tax-calculation, inclusive]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  Taxable value ₹1,00,000 and IGST ₹18,000 (not ₹21,240), using price × 18/118, with
  decimal arithmetic.
---

Our product page shows ₹1,18,000 including 18% GST for an inter-state B2B order. Our code does `gst = price * 0.18` to show the tax. What should the taxable value and GST be, and how do I fix the code?
