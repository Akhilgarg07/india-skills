# Razorpay: verification and webhook handler samples

Algorithms as documented by Razorpay and implemented in the official SDKs
(`razorpay-python` `utility.py`):

| What | Message | Key |
|---|---|---|
| Standard Checkout payment | `order_id + "|" + razorpay_payment_id` | API key secret |
| Subscription payment | `razorpay_payment_id + "|" + subscription_id` | API key secret |
| Payment Link callback | `payment_link_id + "|" + payment_link_reference_id + "|" + payment_link_status + "|" + razorpay_payment_id` | API key secret |
| Webhook | raw request body | webhook secret |

All are hex-encoded HMAC-SHA256, compared in constant time.

## Node.js (Express)

```js
import crypto from "node:crypto";
import express from "express";
import Razorpay from "razorpay";

const rzp = new Razorpay({ key_id: process.env.RZP_KEY_ID, key_secret: process.env.RZP_KEY_SECRET });
const app = express();

const safeEqual = (a, b) => {
  const x = Buffer.from(a, "utf8"), y = Buffer.from(b, "utf8");
  return x.length === y.length && crypto.timingSafeEqual(x, y);
};

// 1) create order (amount in paise, integer)
app.post("/api/orders", express.json(), async (req, res) => {
  const cart = await loadCart(req.user.id);                 // price comes from YOUR db, not the client
  const order = await rzp.orders.create({ amount: cart.totalPaise, currency: "INR",
                                          receipt: cart.id, notes: { cart_id: cart.id } });
  await saveOrder({ cartId: cart.id, rzpOrderId: order.id, amountPaise: order.amount, status: "created" });
  res.json({ order_id: order.id, key_id: process.env.RZP_KEY_ID, amount: order.amount });
});

// 2) verify checkout response
app.post("/api/payments/verify", express.json(), async (req, res) => {
  const { razorpay_payment_id, razorpay_signature, cart_id } = req.body;
  const order = await getOrderByCart(cart_id);              // stored order id, not the client's
  const expected = crypto.createHmac("sha256", process.env.RZP_KEY_SECRET)
    .update(`${order.rzpOrderId}|${razorpay_payment_id}`).digest("hex");
  if (!safeEqual(expected, String(razorpay_signature))) return res.status(400).json({ ok: false });
  const payment = await rzp.payments.fetch(razorpay_payment_id);
  if (payment.order_id !== order.rzpOrderId || payment.amount !== order.amountPaise) {
    return res.status(400).json({ ok: false });
  }
  // fulfil only if payment.status === "captured" (or capture it if you capture manually)
  res.json({ ok: true, status: payment.status });
});

// 3) webhook: RAW body
app.post("/webhooks/razorpay", express.raw({ type: "application/json" }), async (req, res) => {
  const sig = req.get("X-Razorpay-Signature") || "";
  const expected = crypto.createHmac("sha256", process.env.RZP_WEBHOOK_SECRET).update(req.body).digest("hex");
  if (!safeEqual(expected, sig)) return res.status(400).end();
  const eventId = req.get("x-razorpay-event-id");
  if (await alreadyProcessed(eventId)) return res.status(200).end();   // duplicate
  await enqueue(JSON.parse(req.body.toString("utf8")), eventId);        // process async, idempotently
  res.status(200).end();                                                 // fast 2xx
});
```

## Python (Flask)

```python
import hashlib, hmac, os
from flask import Flask, request, abort

app = Flask(__name__)

@app.post("/webhooks/razorpay")
def razorpay_webhook():
    raw = request.get_data()                      # bytes, exactly as received
    expected = hmac.new(os.environ["RZP_WEBHOOK_SECRET"].encode(), raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, request.headers.get("X-Razorpay-Signature", "")):
        abort(400)
    event_id = request.headers.get("x-razorpay-event-id")
    if seen(event_id):
        return "", 200
    enqueue(request.get_json(), event_id)
    return "", 200
```

## Idempotent refund (Python requests)

```python
import uuid, requests
key = str(uuid.uuid5(uuid.NAMESPACE_URL, f"refund:{refund_request.id}"))   # stable per refund request
r = requests.post(f"https://api.razorpay.com/v1/payments/{payment_id}/refund",
                  auth=(KEY_ID, KEY_SECRET),
                  headers={"X-Refund-Idempotency": key},
                  json={"amount": refund_request.amount_paise})
if r.status_code == 409:
    ...  # original still processing: retry later with the SAME key and body
```

## State handling sketch

```
order: created -> attempted -> paid
payment: created -> authorized -> captured -> refunded (partial/full)
                 \-> failed
```
- Apply transitions only forward. Ignore a late `payment.authorized` after `captured`.
- `order.paid` stays `paid` even after a refund, so track refunds separately.
