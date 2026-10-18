---
description: Generate a dynamic UPI QR for a web checkout.
tags: [upi-payments, qr]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  Builds upi://pay with pa, pn (percent-encoded &), am=1499.00, cu=INR, unique tr, tn;
  renders the URI as a QR; confirms payment server-side via webhook/status API, never
  from client; handles pending.
---

Build a Node.js endpoint for our web checkout that shows a UPI QR code for order #A1001 of ₹1,499.00 to our merchant UPI ID payments@okicici (business name: Kiran Traders & Co). How do we know when the customer has paid?
