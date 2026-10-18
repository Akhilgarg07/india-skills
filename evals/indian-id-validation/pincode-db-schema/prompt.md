---
description: Address table design with a PIN code column; tests string storage and format rules.
tags: [indian-id-validation, pincode]
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  PIN code stored as a 6-character string with a CHECK constraint ^[1-9][0-9]{5}$,
  not an integer; explains that format validity does not mean the PIN exists.
---

Write a PostgreSQL table for Indian customer addresses. I was going to make `pincode INTEGER NOT NULL`. Add sensible constraints.
