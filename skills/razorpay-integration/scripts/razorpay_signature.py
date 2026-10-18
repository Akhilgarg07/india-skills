#!/usr/bin/env python3
"""Razorpay signature verification and amount helpers, matching Razorpay's docs and
official SDKs (razorpay-python utility.py):

  checkout payment   HMAC_SHA256(key_secret,  order_id + "|" + razorpay_payment_id)
  subscription       HMAC_SHA256(key_secret,  razorpay_payment_id + "|" + subscription_id)
  payment link       HMAC_SHA256(key_secret,  payment_link_id + "|" + reference_id + "|"
                                              + status + "|" + razorpay_payment_id)
  webhook            HMAC_SHA256(webhook_secret, RAW request body bytes)
                     compared with the X-Razorpay-Signature header (hex digest)

Always compare with hmac.compare_digest (constant time). For checkout payments use the
order_id stored on YOUR server, not the razorpay_order_id echoed back by the browser.

Module usage:
    >>> from razorpay_signature import verify_payment, rupees_to_paise, sign
    >>> sig = sign("order_9A33XWu170gUtm|pay_29QQoUBi66xm2f", "secret")
    >>> verify_payment("order_9A33XWu170gUtm", "pay_29QQoUBi66xm2f", sig, "secret")
    True
    >>> rupees_to_paise("499.99")
    49999

CLI usage (secrets come from environment variables, never from argv):
    RAZORPAY_KEY_SECRET=... python3 razorpay_signature.py payment ORDER_ID PAYMENT_ID SIGNATURE
    RAZORPAY_WEBHOOK_SECRET=... python3 razorpay_signature.py webhook body.json SIGNATURE
    python3 razorpay_signature.py paise 1499.50

Standard library only.
"""

import hashlib
import hmac
import os
import sys
from decimal import Decimal, InvalidOperation


def sign(message, secret) -> str:
    """Hex HMAC-SHA256 of message (str or bytes) with secret (str or bytes)."""
    if isinstance(message, str):
        message = message.encode("utf-8")
    if isinstance(secret, str):
        secret = secret.encode("utf-8")
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


def _verify(message, signature, secret) -> bool:
    if not signature or not secret:
        return False
    return hmac.compare_digest(sign(message, secret), str(signature).strip().lower())


def verify_payment(order_id: str, payment_id: str, signature: str, key_secret: str) -> bool:
    """Standard Checkout: order_id (from your DB) + '|' + razorpay_payment_id."""
    return _verify(f"{order_id}|{payment_id}", signature, key_secret)


def verify_subscription(payment_id: str, subscription_id: str, signature: str, key_secret: str) -> bool:
    """Subscriptions: razorpay_payment_id + '|' + subscription_id."""
    return _verify(f"{payment_id}|{subscription_id}", signature, key_secret)


def verify_payment_link(payment_link_id, reference_id, status, payment_id, signature, key_secret) -> bool:
    """Payment Links callback: link_id|reference_id|status|payment_id."""
    return _verify(f"{payment_link_id}|{reference_id}|{status}|{payment_id}", signature, key_secret)


def verify_webhook(raw_body: bytes, signature: str, webhook_secret: str) -> bool:
    """Webhook: HMAC over the RAW body bytes. Do not json.loads() + json.dumps() first."""
    if isinstance(raw_body, str):
        raise TypeError("pass the raw request body as bytes, exactly as received")
    return _verify(raw_body, signature, webhook_secret)


def rupees_to_paise(amount) -> int:
    """'1,499.50' / Decimal('1499.5') -> 149950. Rejects floats and sub-paise precision."""
    if isinstance(amount, float):
        raise TypeError("pass rupees as str or Decimal, not float")
    try:
        d = Decimal(str(amount).replace(",", "").replace("₹", "").strip())
    except InvalidOperation:
        raise ValueError(f"{amount!r} is not a number") from None
    if not d.is_finite() or d <= 0:
        raise ValueError("amount must be a positive number")
    paise = d * 100
    if paise != paise.to_integral_value():
        raise ValueError("amount has more than 2 decimal places")
    return int(paise)


def paise_to_rupees(paise: int) -> Decimal:
    if not isinstance(paise, int) or isinstance(paise, bool):
        raise TypeError("paise must be an int")
    return (Decimal(paise) / 100).quantize(Decimal("0.01"))


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) == 2 and argv[0] == "paise":
        try:
            print(rupees_to_paise(argv[1]))
        except (TypeError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        return 0
    if len(argv) == 4 and argv[0] == "payment":
        secret = os.environ.get("RAZORPAY_KEY_SECRET")
        if not secret:
            print("set RAZORPAY_KEY_SECRET in the environment", file=sys.stderr)
            return 2
        ok = verify_payment(argv[1], argv[2], argv[3], secret)
    elif len(argv) == 3 and argv[0] == "webhook":
        secret = os.environ.get("RAZORPAY_WEBHOOK_SECRET")
        if not secret:
            print("set RAZORPAY_WEBHOOK_SECRET in the environment", file=sys.stderr)
            return 2
        with open(argv[1], "rb") as fh:
            ok = verify_webhook(fh.read(), argv[2], secret)
    else:
        print(__doc__.split("CLI usage")[1].split("Standard library")[0].strip(), file=sys.stderr)
        return 2
    print("signature valid" if ok else "signature INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
