---
description: Income-tax year selector after the Income-tax Act 2025.
tags: [indian-dates-and-fiscal-year, tax-year]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  FY 2025-26 income → AY 2026-27 under 1961 Act; FY 2026-27 income → Tax Year 2026-27
  under 2025 Act (no AY); labels must show income period to avoid '2026-27' ambiguity.
---

Our tax-filing app has a dropdown 'Assessment Year: 2026-27, 2027-28'. With the new Income-tax Act, what should the options and labels be for income earned in FY 2025-26 and FY 2026-27?
