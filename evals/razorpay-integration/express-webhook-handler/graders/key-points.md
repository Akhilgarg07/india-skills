---
type: llm
---

PASS only if the response does ALL of the following:
1. Verifies the X-Razorpay-Signature header as an HMAC-SHA256 hex digest computed with the webhook secret (not the API key secret).
2. Computes the HMAC over the raw request body (e.g. express.raw() for this route, or capturing the raw buffer), and explains that the global express.json() / JSON.stringify(req.body) would break verification.
3. De-duplicates events using the x-razorpay-event-id header (idempotent processing).
4. Handles out-of-order or repeated events safely (e.g. never moving a captured/paid order backwards) and returns a 2xx quickly, doing heavy work asynchronously.
5. Uses a constant-time comparison (crypto.timingSafeEqual or equivalent) or the official SDK's validateWebhookSignature with the raw body.

FAIL if the signature is computed over JSON.stringify(req.body) or with the API key secret.
