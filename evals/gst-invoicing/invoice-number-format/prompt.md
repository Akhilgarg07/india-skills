---
description: Invoice numbering rules.
tags: [gst-invoicing, rule-46]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  No: max 16 characters, only letters, digits, hyphen and slash (no '#'), consecutive
  and unique within the financial year (April-March); suggest a compliant format.
---

We want our invoice numbers to look like `ACME-INVOICE#2026/10/18-000123` and reset to 1 every month. Is that OK for GST invoices in India?
