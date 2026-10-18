# Sources: razorpay-integration

**Last verified: 2026-10-18**

All facts below are from Razorpay's official documentation and official SDK source,
downloaded and read on the date above (**[page]**). Razorpay also publishes LLM-friendly
Markdown copies of its docs under https://razorpay.com/docs/build/llm-docs/ (index:
https://razorpay.com/docs/llms.txt).

- [page] Validate and Test Webhooks: X-Razorpay-Signature, HMAC-SHA256 with webhook secret
  over the raw body, "Do not parse or cast the webhook request body", old secret for retries
  after rotation, x-razorpay-event-id idempotency, out-of-order events, blacklisted test
  domains. https://razorpay.com/docs/webhooks/validate-test/
- [page] Webhooks Best Practices: non-2xx = failure, exponential back-off retries for 24
  hours, then disabled; at-least-once delivery; 5-second timeout; TLS 1.2+.
  https://razorpay.com/docs/webhooks/best-practices/
- [page] Payments webhook events list (payment.authorized, payment.captured, payment.failed,
  order.paid, ...). https://razorpay.com/docs/build/llm-docs/webhooks/payments.md
- [page] Orders API, Create an Order: amount in smallest sub-unit, currency, receipt (max 40,
  unique), notes (15 pairs, 256 chars), order statuses created/attempted/paid.
  https://razorpay.com/docs/api/orders/create/
- [page] Standard Checkout integration steps: payments without order_id cannot be captured and
  are auto-refunded; verify signature `hmac_sha256(order_id + "|" + razorpay_payment_id, secret)`
  using the server's order_id; callback_url vs handler; verify payment status.
  https://razorpay.com/docs/build/llm-docs/payments/payment-gateway/web-integration/standard/integration-steps.md
- [page] Standard Checkout best practices: capture settings, Orders API, signature verification,
  check captured/paid before providing services, webhooks payment.captured / payment.failed /
  order.paid, callback URL for non-iframe browsers.
  https://razorpay.com/docs/build/llm-docs/payments/payment-gateway/web-integration/standard/best-practices.md
- [page] About Payments (states; authorized payments auto-refunded if not captured within 3 days)
  and Payment Capture Settings. https://razorpay.com/docs/build/llm-docs/payments/payments.md ,
  https://razorpay.com/docs/build/llm-docs/payments/payments/capture-settings.md
- [page] Refunds overview (normal/instant/batch, states, source refunds, 6-month limit for normal
  refunds, processed before ARN), Normal Refunds (timelines by method), refund webhooks.
  https://razorpay.com/docs/build/llm-docs/payments/refunds.md ,
  https://razorpay.com/docs/build/llm-docs/payments/refunds/normal.md ,
  https://razorpay.com/docs/build/llm-docs/payments/refunds/subscribe-to-webhooks.md
- [page] Create a Normal Refund (Idempotent Request): `X-Refund-Idempotency`, key ≥ 10 chars of
  letters/digits/hyphens/underscores, same body on retry, 409 while in progress.
  https://razorpay.com/docs/build/llm-docs/api/refunds/normal-refunds-idempotent.md
- [page] Official Python SDK, `razorpay/utility/utility.py` (payment, subscription, payment link
  and webhook signature formats; hmac.compare_digest).
  https://github.com/razorpay/razorpay-python/blob/master/razorpay/utility/utility.py

Note: Razorpay's own pages give different normal-refund timelines (5-7 and 7-10 working days);
the skill says "several working days" and quotes both.
