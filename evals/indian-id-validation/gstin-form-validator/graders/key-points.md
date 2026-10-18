---
type: llm
---

PASS only if the response does ALL of the following:
1. Implements the GSTIN check-character (mod-36 weighted checksum over the first 14 characters) and compares it with the 15th character.
2. Explains that the regex wrongly requires 'Z' as the 14th character, and that GSTINs such as 27AABCI2726B1CD with another letter there are legitimate.
3. Checks the first two digits against GST state codes (not just any two digits).
4. Says that passing validation proves only the format; registration/active status needs a GST portal or API lookup.

FAIL if any of these is missing, or if the code still rejects 27AABCI2726B1CD.
