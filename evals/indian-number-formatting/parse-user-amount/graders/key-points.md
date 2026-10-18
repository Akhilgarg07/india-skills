---
type: llm
---

PASS only if the response does ALL of the following:
1. Strips the ₹ symbol, 'Rs'/'Rs.'/'INR' prefixes, the '/-' suffix, spaces and commas before parsing.
2. Parses into Decimal (or integer paise) instead of float for money.
3. Does not enforce Western or Indian comma positions (accepts both '1,20,000' and '120,000').
4. Returns a clear validation error for anything else (e.g. '1.2 lakh' unless explicitly supported).

FAIL if the solution still uses float for the parsed amount.
