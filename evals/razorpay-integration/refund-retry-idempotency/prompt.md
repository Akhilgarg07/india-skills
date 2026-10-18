---
description: Safe refund retries.
tags: [razorpay-integration, refund]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  Use X-Refund-Idempotency header with a stable key per refund request (≥10 chars,
  alnum/-/_), identical body on retry, handle 409 in-progress; track refund webhooks;
  amount in paise.
---

Our refund job calls Razorpay's refund API and retries on timeouts. Twice this month a customer got refunded twice. How do we fix it?
