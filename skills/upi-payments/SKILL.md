---
name: upi-payments
description: Build and handle UPI payments correctly - upi://pay deep links and intent URIs (pa, pn, am, cu, tn, tr, mc, mode parameters per NPCI's UPI Linking Specification), UPI QR codes (static vs dynamic), VPA/UPI ID format checks, and payment-status best practices (server-side verification, pending states, NPCI status-check limits, end of P2P collect requests). Use when adding "Pay with UPI" buttons, generating UPI QR codes, parsing scanned UPI QRs, writing payment confirmation or reconciliation logic, or reviewing UPI-related code in Indian apps. Includes a stdlib Python link builder/parser.
license: MIT
metadata:
  version: "0.1.0"
  last-verified: "2026-10-18"
---

# UPI payments

UPI (Unified Payments Interface) is run by NPCI and regulated by RBI. Apps don't talk to UPI
directly; payments go through a **PSP / bank or a payment gateway**. This skill covers the
parts developers build themselves: payment links/QRs and status handling.

## The `upi://pay` URI

```
upi://pay?pa=merchant@okbank&pn=Asha%20Stores&am=149.50&cu=INR&tn=Order%201001&tr=ORD1001
```

| Param | Meaning | Static QR | Dynamic link/QR |
|---|---|---|---|
| `pa` | Payee VPA (UPI ID) | **M** | **M** |
| `pn` | Payee name (shown to payer) | **M** | **M** |
| `am` | Amount, decimal (`149.50`). If absent, the payer types it | O | **M** |
| `cu` | Currency. Only `INR` | O | O |
| `tr` | Your transaction/order reference (order no., bill id) | O | **M for merchants** |
| `tn` | Short note shown to payer | O | O |
| `mc` | Merchant category code (pass as given by your bank/PSP) | O | O |
| `tid` | PSP-generated transaction id (pass as given) | O | O |
| `mam` | Minimum amount, if part payment is allowed | O | C |
| `url` | http(s) link to the bill/order details. Must relate to this transaction | O | O |
| `mode` | Initiation mode: `01` QR, `02` secure QR, `04` intent, `05` secure intent ... | see below | |

- Percent-encode values (`%20` for spaces, `%26` for `&`). Don't use `+` for spaces; some apps
  show it literally. Don't put `&`, `?` or `#` unencoded in `pn`/`tn`.
- Amount: plain decimal, no `₹`, no commas, at most 2 decimals, > 0.
- Use a **unique `tr` per payment attempt** and store it. It is how you reconcile.
- **Signed intents/QRs:** NPCI's spec also defines `mode`, `orgid`, `mid`/`msid`/`mtid` and a
  `sign` field (RSA signature over the URI, `sign` last) for verified merchant intents. Merchants
  normally get these from their acquiring bank/gateway. Never invent `mc`, `tid`, `orgid` or
  `sign` values. How payer apps treat unsigned merchant-style links varies by app
  (`TODO(verify)` current NPCI rules on unsigned intents).
- Full parameter table and caveats: [references/upi-params.md](references/upi-params.md).

### Intent (Android) vs link vs QR
- **Android:** fire an `ACTION_VIEW` intent with the `upi://pay?...` URI. The OS shows the UPI app
  chooser. The app result (`Status=SUCCESS` etc.) is **untrusted**; only use it to trigger a
  server-side status check.
- **iOS:** don't rely on an app chooser for `upi://`; behaviour depends on which UPI apps are
  installed. Prefer a gateway SDK or show a QR.
- **Desktop/web:** show a **QR** of the same URI and poll your backend for status.

## UPI QR codes
- A UPI QR **is the `upi://pay` URI encoded as a QR code**. Nothing else goes in the payload.
- **Static QR** (shop counter): `pa`, `pn` (+ `mc`), no `am`/`tr`. The payer enters the amount, and
  you reconcile by time and amount, which is weak. Prefer **dynamic QR** (per order: `am` + unique `tr`).
- Python has no standard-library QR encoder: generate the URI with `scripts/upi_link.py`, then
  render it with a QR library (`qrcode` in Python, `qrcode`/`qrcode.react` in JS, ZXing on
  Android). Use error-correction level M or higher and a quiet zone. Show payee name and amount
  as text beside the QR.
- When **scanning** a UPI QR, parse it with a URL parser, show `pn`, `pa` and `am` to the user
  before paying, and reject non-`upi://pay` payloads.

## VPA (UPI ID) format
- Shape: `handle@psp`, e.g. `name.surname@okaxis`, `9876543210@ybl`. One `@`; the part after it
  is the PSP handle.
- Format checks only catch typos. To confirm a VPA exists and see the registered name, use your
  PSP/gateway's **VPA validation** API. Show the returned name to the user before paying out.
- Don't lowercase or otherwise rewrite user input silently. Trim whitespace and show errors.
- NPCI doesn't publish a public character grammar; `scripts/upi_link.py vpa` applies a
  pragmatic check (letters, digits, `.`, `_`, `-` before `@`).

## Payment status: rules
1. **Never mark an order paid from the client.** The intent callback, a redirect, or "I have paid"
   are not proof. Confirm through your PSP/gateway **webhook** (signature-verified) and/or a
   **server-side status API** call keyed by your `tr`/order id.
2. Model states explicitly: `CREATED → PENDING → SUCCESS | FAILED | EXPIRED`, plus
   `REFUNDED`/`DISPUTED`. UPI payments can stay **pending** (bank timeouts) and resolve later. Don't
   fail them early or let the user pay twice. Show "payment pending" and resolve asynchronously.
3. **Status-check etiquette:** NPCI has capped how often apps call the check-status API (reported:
   at most 3 checks per transaction, at least 90 seconds apart, from 1 Aug 2025). Prefer webhooks;
   poll with back-off; don't call status in a tight loop. `TODO(verify)` exact limits against the
   NPCI circular.
4. **Idempotency:** one order id → one active payment request. Webhooks can arrive late, twice or
   out of order. Make handlers idempotent and keep the first terminal state unless a refund event follows.
5. **Verify amount and payee** in the webhook/status response against your order before
   fulfilment (amount tampering, wrong `tr`).
6. **Reconcile daily** against gateway settlement reports. Auto-refund duplicate or late
   payments for expired orders.
7. **Collect requests:** NPCI directed that no **P2P collect** request be initiated or processed
   after 1 Oct 2025 (circular of 29 Jul 2025, as reported; anti-fraud).
   Don't build "request money from a friend" flows on collect. **Merchant** collect flows
   continue, but intent/QR flows are preferred.

## Limits (don't hard-code)
- **P2P:** ₹1 lakh per transaction (RBI). **P2M:** generally ₹1 lakh, with higher limits (₹2 lakh /
  ₹5 lakh) for specific categories such as hospitals and education. Since April 2025, RBI lets NPCI
  set P2M limits, and banks can set lower limits. Treat limits as config and handle "limit exceeded"
  errors gracefully.

## Script

```bash
python3 scripts/upi_link.py build --pa merchant@okbank --pn "Asha Stores" --am 149.50 --tr ORD1001 --tn "Order 1001"
python3 scripts/upi_link.py parse "upi://pay?pa=merchant@okbank&pn=Asha%20Stores&am=149.50" --dynamic
python3 scripts/upi_link.py vpa someone@okaxis
```
Module: `build_upi_link(pa, pn, am=, tr=, tn=, ...)` (raises `ValueError` listing every problem),
`parse_upi_link(uri, dynamic=)`, `validate_vpa(vpa)`.

For gateway-specific integration (orders, webhooks, refunds) see the `razorpay-integration` skill.
Sources: [references/sources.md](references/sources.md).
