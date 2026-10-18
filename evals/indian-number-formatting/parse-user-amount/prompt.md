---
description: Parsing amounts typed by Indian users.
tags: [indian-number-formatting, parse]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  Strip ₹/Rs/INR, '/-', commas and spaces; parse with Decimal; do not validate comma
  positions; explicit error for unsupported words like 'lakh'.
---

Users type amounts like '1,20,000', 'Rs. 1,20,000/-', '₹ 1,20,000' and '120000' into our Python form. Our parser does float(value.replace(',', '')) and crashes on some. Fix it.
