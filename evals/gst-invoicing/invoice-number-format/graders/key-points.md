---
type: llm
---

PASS only if the response does ALL of the following:
1. Says invoice numbers can be at most 16 characters, so this format is too long.
2. Says only letters, digits, hyphen (-) and slash (/) are allowed, so '#' is not permitted.
3. Says numbers must be consecutive and unique for the financial year (April to March), so a monthly reset that repeats numbers within the FY is not allowed unless the series stays unique (e.g. by including the month in a series prefix).
4. Proposes a compliant example of 16 characters or fewer, such as INV/26-27/000123.

FAIL if the answer approves the proposed format.
