---
description: Trusting the UPI app intent response.
tags: [upi-payments, status]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  Yes: the intent response is untrusted/spoofable and can be wrong; use it only to
  trigger server-side verification via gateway webhook/status API; handle pending;
  idempotency; verify amount/payee.
---

In our Android app we launch a UPI intent and, when the result Intent has Status=SUCCESS, we immediately mark the order as paid and ship it. Any problem with that?
