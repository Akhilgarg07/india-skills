---
type: llm
---

PASS only if the response does ALL of the following:
1. Explains that the first two digits identify a postal circle/sub-region, not a state, so a prefix table can't reliably give the state.
2. Gives at least one concrete mismatch example (e.g. Telangana PINs in the Andhra Pradesh range, Chandigarh's 160xxx in the Punjab range, Uttarakhand within the Uttar Pradesh range).
3. Recommends the official All India Pincode Directory (India Post data on data.gov.in) for PIN → state/district lookup.
4. Recommends warning or suggesting instead of rejecting the form on mismatch.

FAIL if the answer endorses rejecting forms based on a two-digit prefix table.
