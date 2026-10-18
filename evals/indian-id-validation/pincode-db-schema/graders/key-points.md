---
type: llm
---

PASS only if the response does ALL of the following:
1. Stores the PIN code as text (CHAR(6)/VARCHAR/TEXT), not INTEGER, and explains why (it is an identifier; never do arithmetic on it).
2. Adds a constraint equivalent to exactly 6 digits with the first digit 1-9 (e.g. CHECK (pincode ~ '^[1-9][0-9]{5}$')).
3. Mentions that a format-valid PIN may still not exist, and that existence or state lookup needs the India Post PIN directory.

FAIL if the column remains an integer type.
