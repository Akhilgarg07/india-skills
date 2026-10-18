---
description: Quick format check of an IFSC with letter O and a PAN with a bad status letter.
tags: [indian-id-validation, ifsc, pan]
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  Both are invalid: the IFSC has the letter O in position 5 where the digit zero is
  required; the PAN's 4th character X is not a valid holder-status code.
---

A customer typed these into our payout form. Are they valid? IFSC: RBISONDPA01, PAN: ABCXE1234F
