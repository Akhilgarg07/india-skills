---
type: llm
---

PASS only if the response does ALL of the following:
1. Recommends the X-Refund-Idempotency header with a stable idempotency key per logical refund request (e.g. derived from your refund record id), reused on every retry.
2. Says retries must send the same request body as the original (a different body with the same key is rejected).
3. Mentions handling a 409 response (original still in progress) by retrying later with the same key, and/or reconciling with refund.processed / refund.failed webhooks or fetching refunds for the payment before retrying.
4. Notes the key format requirement (at least 10 characters of letters, digits, hyphens, underscores) or recommends a UUID.

FAIL if the answer only suggests reducing retries without idempotency keys.
