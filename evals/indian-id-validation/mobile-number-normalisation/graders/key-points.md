---
type: llm
---

PASS only if the response does ALL of the following:
1. Strips spaces/hyphens and accepts the +91, 91 and leading-0 prefixes, so both "+91 98765-43210" and "09876543210" are accepted.
2. Requires the 10-digit national number to start with 6, 7, 8 or 9, so "1234567890" is rejected.
3. Recommends storing one normalised form, E.164 (+919876543210).
4. Notes that format validation does not prove the number is active or belongs to the user (e.g. verify by OTP).

FAIL if "1234567890" would still be accepted.
