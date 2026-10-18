---
description: Design an Indian checkout address form.
tags: [indian-addresses, form]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  PIN 6 digits first digit 1-9 as string; flexible lines; landmark field; state/UT
  dropdown with all 28 states + 8 UTs; PIN autofill suggest not overwrite; mobile; no
  strict street requirement.
---

Design the address form (fields, validation rules, and a JSON schema) for our e-commerce checkout in India. We currently copy our US form: Street, City, State (dropdown), ZIP (5 digits).
