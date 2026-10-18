---
name: razorpay-integration
description: Integrate Razorpay payments correctly per Razorpay's official docs - server-side Orders API (amount in paise, receipt, notes), Standard Checkout, payment signature verification (order_id|payment_id HMAC-SHA256), capture within 3 days, webhook signature verification on the raw body (X-Razorpay-Signature), duplicate/out-of-order webhook handling (x-razorpay-event-id), and refunds with X-Refund-Idempotency. Use when adding Razorpay checkout to a web/mobile app, writing payment callback or webhook handlers, implementing refunds, or reviewing Razorpay integration code for security bugs. Includes stdlib Python signature/amount helpers.
license: MIT
metadata:
  version: "0.1.0"
  last-verified: "2026-10-18"
---

# Razorpay integration

Follow Razorpay's official docs (https://razorpay.com/docs/). This skill condenses the parts that
are easy to get wrong. Prefer the official SDKs (`razorpay` for Node, Python, PHP, Java, Ruby,
.NET, Go) for API calls.

## The safe Standard Checkout flow

```
browser ──(1) "buy"──> your server ──(2) POST /v1/orders──> Razorpay
browser <─(3) order_id + key_id ── your server
browser ──(4) Checkout(order_id) ─> Razorpay ─> handler(payment_id, order_id, signature)
browser ──(5) POST ids+signature──> your server: verify signature with STORED order_id
Razorpay ──(6) webhook payment.captured / order.paid ──> your server (verify, idempotent)
your server: fulfil only when payment is captured / order is paid, amount matches
```

1. **Create an order on the server** for every checkout. `amount` is an **integer in the smallest
   currency unit** (₹499.00 → `49900` paise), `currency: "INR"`, `receipt` (your reference, **max 40
   chars, unique**), `notes` (max 15 key-value pairs, 256 chars each). Payments made **without an
   `order_id` cannot be captured and are auto-refunded**.
2. Send only `key_id` and `order_id` to the client. **`key_secret` never leaves the server.**
   Test and live keys are different; mixing them gives "id provided does not exist" errors.
3. Checkout's success handler returns `razorpay_payment_id`, `razorpay_order_id`,
   `razorpay_signature`. The browser result is **not proof** of payment.
4. **Verify the signature on the server**:
   `hex(HMAC_SHA256(key_secret, order_id + "|" + razorpay_payment_id)) == razorpay_signature`,
   where `order_id` is the one **you stored** for this checkout, not the one the browser sent.
   Use a constant-time comparison.
5. **Check status before fulfilment**: payment `captured` and order `paid` (Fetch Payment / Fetch
   Order APIs, or webhooks). Compare amount and currency with your order.
6. **Capture**: an `authorized` payment must be captured **within 3 days** or Razorpay auto-refunds
   it. Enable auto-capture in Dashboard payment capture settings, or call the capture API yourself.
7. Use `callback_url` only for WebView/redirect flows (and browsers without iframe support, such as
   in-app browsers); standard web uses the `handler` function plus webhooks.

## Webhooks

- Signature: header **`X-Razorpay-Signature`** = hex **HMAC-SHA256 of the raw request body** with the
  **webhook secret** (set per webhook in the Dashboard; *not* the API key secret).
- **Use the raw body bytes.** Don't parse and re-serialise JSON before verifying (key order and
  whitespace change the HMAC). In Express use `express.raw({type: "application/json"})` on that
  route. In Django use `request.body`. In Flask use `request.get_data()`.
- **Duplicates are expected** (at-least-once delivery). De-duplicate on the **`x-razorpay-event-id`**
  header; store processed ids.
- **Order is not guaranteed** (`payment.captured` may arrive before `payment.authorized`). Make
  state transitions monotonic (never go from `captured` back to `authorized`).
- Respond **2xx quickly** (Razorpay treats non-2xx or a slow response, around 5 s, as failure) and
  do heavy work async. Failed deliveries are retried with exponential back-off for **24 hours**. Then
  the webhook is **disabled** until you re-enable it.
- After rotating the webhook secret, verify retries of older events with the **old** secret.
- Subscribe at least to `payment.captured`, `payment.failed`, `order.paid`; for refunds
  `refund.processed`, `refund.failed` (also `refund.created`, `refund.speed_changed`).
- Endpoint must be HTTPS with TLS 1.2+. Razorpay rejects some webhook URLs (localhost,
  `ngrok.io`, `webhook.site`, `requestbin.com` ...). Use a staging URL for testing.

## Refunds

- `POST /v1/payments/:payment_id/refund` with `amount` in paise (partial refunds allowed). Normal
  refunds take several working days, and Razorpay's pages quote different ranges (5-7 or 7-10; for UPI
  2-7 days). Instant refunds are a separate option.
- **Idempotency:** send header **`X-Refund-Idempotency: <key>`**. The key must be at least 10 chars
  of letters, digits, `-`, `_`, e.g. a UUID derived from your refund request id. Retries must reuse
  the **same key and identical body**. A different body with the same key gets `BAD_REQUEST`, and a
  concurrent in-flight request gets **409** (retry later).
- Refunds go back to the **original payment method** (source refunds). Normal refunds fail for
  payments **older than 6 months**.
- A refund may show `processed` before the bank ARN/RRN arrives. Track `refund.processed` /
  `refund.failed` webhooks and store `acquirer_data.arn` when present.

## Common bugs to flag in reviews

- Amount sent in rupees or as a float (`499.0`) instead of integer paise. Rounding with floats.
- Fulfilling on the client `handler` success without server-side verification.
- Verifying against `razorpay_order_id` from the request instead of the stored order id.
- `==` string comparison of signatures (use `hmac.compare_digest` / `crypto.timingSafeEqual`).
- Webhook verified against `JSON.stringify(req.body)` instead of the raw body.
- `key_secret` or webhook secret in frontend code, mobile apps, logs or git.
- No de-duplication on `x-razorpay-event-id`; non-idempotent refund retries.
- Not handling `authorized` but uncaptured payments (auto-refunded after 3 days).
- One order reused across carts or amounts. Create a new order when the amount changes.

## Script

```bash
python3 scripts/razorpay_signature.py paise 1,499.50                          # -> 149950
RAZORPAY_KEY_SECRET=... python3 scripts/razorpay_signature.py payment ORDER_ID PAYMENT_ID SIG
RAZORPAY_WEBHOOK_SECRET=... python3 scripts/razorpay_signature.py webhook raw_body.json SIG
```
Module: `verify_payment`, `verify_subscription`, `verify_payment_link`, `verify_webhook(raw_bytes, ...)`,
`sign`, `rupees_to_paise`, `paise_to_rupees`. Code samples for Node/Python handlers:
[references/webhooks-and-verification.md](references/webhooks-and-verification.md).
Sources: [references/sources.md](references/sources.md).

For UPI-specific concerns (intent/QR, pending states) see the `upi-payments` skill.
