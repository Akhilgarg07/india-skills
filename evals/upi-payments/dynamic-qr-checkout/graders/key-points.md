---
type: llm
---

PASS only if the response does ALL of the following:
1. Builds a upi://pay URI with pa=payments@okicici, a properly percent-encoded pn (the '&' encoded as %26 and spaces as %20, not '+'), am=1499.00 with no commas or ₹ sign, cu=INR, and a unique tr transaction/order reference.
2. Explains that the UPI QR code simply encodes this URI, rendered with a QR library.
3. Says payment must be confirmed server-side (payment gateway/PSP webhook or status API keyed by the order reference), never from the client or because the QR was scanned.
4. Handles a pending state and/or polls with back-off rather than tight loops, and verifies amount and reference before marking the order paid.

FAIL if the answer marks the order paid based on a client-side event, or builds the link with an unencoded '&' in pn.
