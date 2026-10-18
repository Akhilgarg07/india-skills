---
type: llm
---

PASS only if the response does ALL of the following:
1. Provides a format check requiring exactly one '@', a non-empty handle part (letters, digits, dot, underscore, hyphen) and a PSP handle after '@'.
2. Says a regex only catches typos and cannot confirm the VPA exists or belongs to the user.
3. Recommends verifying through the payment gateway/PSP VPA validation API and showing the registered name to the user for confirmation before sending money.

FAIL if the answer says regex validation alone is sufficient before payouts.
