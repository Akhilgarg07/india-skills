---
type: llm
---

PASS only if the response does ALL of the following:
1. Says India has 28 states and 8 union territories, and that Jammu and Kashmir is now a union territory, with Ladakh a separate UT (since 31 October 2019).
2. Says Dadra and Nagar Haveli and Daman and Diu were merged into one UT (from January 2020).
3. Updates the names: Orissa → Odisha, Uttaranchal → Uttarakhand, Pondicherry → Puducherry, while accepting old names as input aliases.
4. Suggests storing a stable code (e.g. the 2-digit GST state code) alongside the name.

FAIL if the answer keeps Jammu and Kashmir as a state or keeps the two merged UTs separate.
