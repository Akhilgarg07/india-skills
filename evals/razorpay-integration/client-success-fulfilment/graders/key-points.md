---
type: llm
---

PASS only if the response does ALL of the following:
1. Says an order must be created on the server via the Orders API and its order_id passed to Checkout (payments without an order_id cannot be captured and are auto-refunded).
2. Says the amount must be in paise as an integer (₹499 = 49900), not 499.
3. Requires server-side verification of razorpay_signature as HMAC-SHA256 of order_id + '|' + razorpay_payment_id with the key_secret, using the order_id stored on the server.
4. Requires confirming payment status (captured / order paid) and the amount via the Razorpay API or webhooks before shipping, and mentions capture (auto-capture or within 3 days).

FAIL if the answer approves fulfilling directly from the client callback.
