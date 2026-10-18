---
type: llm
---

PASS only if the response does ALL of the following:
1. Says the intent result (Status=SUCCESS) is not proof of payment, because it can be spoofed, malformed, or differ from the final state.
2. Recommends confirming via a server-side source of truth (PSP/gateway webhook with signature verification or a server-side status check) before shipping.
3. Mentions pending/timeout states that resolve later, and idempotent handling of duplicate or late webhooks.
4. Mentions verifying amount and order reference in the confirmed status against the order.

FAIL if the answer says trusting Status=SUCCESS is fine.
