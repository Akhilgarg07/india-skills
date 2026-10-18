---
description: VPA validation before payouts.
tags: [upi-payments, vpa]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  Pragmatic format check (one @, handle chars, PSP handle), no silent rewriting; regex
  is not enough: use the PSP/gateway VPA validation API to confirm existence and show
  the registered name before payout.
---

Users enter their UPI ID for refunds/payouts. Write a TypeScript validator, and tell me if the regex is enough before we send money.
