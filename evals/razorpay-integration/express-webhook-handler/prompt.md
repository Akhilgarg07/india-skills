---
description: Writing a secure Razorpay webhook endpoint in Express.
tags: [razorpay-integration, webhook]
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  Verifies X-Razorpay-Signature as HMAC-SHA256 of the RAW body with the webhook secret
  (express.raw on that route), constant-time compare, dedupe on x-razorpay-event-id,
  handles out-of-order events, responds 2xx fast.
---

Write an Express.js endpoint that receives Razorpay webhooks and marks orders as paid. We use app.use(express.json()) globally.
