---
type: llm
---

PASS only if the response does ALL of the following:
1. Replaces ZIP with a 6-digit PIN code (first digit 1-9), stored as a string.
2. Includes a landmark field and flexible address lines that do not require a street name or house-number format.
3. Uses a 'State / UT' dropdown that covers all 28 states and 8 union territories (current names such as Odisha and Puducherry, with J&K and Ladakh as UTs).
4. Uses PIN code to suggest or autofill city/district/state but lets the user edit, and does not hard-reject on PIN/state mismatch without an authoritative directory check.
5. Includes a mobile number field suitable for Indian numbers (10 digits / +91).

FAIL if the form keeps a 5-digit ZIP or omits union territories from the state list.
