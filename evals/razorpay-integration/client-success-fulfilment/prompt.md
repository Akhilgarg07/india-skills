---
description: Fulfilling on the Checkout handler without verification.
tags: [razorpay-integration, checkout, security]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  Create order server-side (amount in paise, 49900), pass order_id; verify
  razorpay_signature server-side using stored order_id + '|' + payment_id with
  key_secret; check captured/paid and amount via API or webhook; capture within 3 days.
---

Our React app opens Razorpay Checkout with amount 499 and our key, and in the handler callback we call /api/fulfil?payment_id=... which ships the product. Review this flow.
