---
description: Amount-in-words for an invoice template.
tags: [indian-number-formatting, words]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  Uses thousand/lakh/crore (not million), handles paise ('and Fifty Paise'), 'Only'
  suffix, singular Rupee/Paisa, rounds to paise from string/decimal not float, handles
  crore and above (e.g. 'One Hundred Crore').
---

Write a TypeScript function amountInWords(amount: string) for our Indian invoices. 120000 should print as "One Lakh Twenty Thousand Rupees Only" and 1050.50 should include paise.
