---
type: llm
---

PASS only if the response does ALL of the following:
1. Explains that new Date('01/04/2026') is parsed as MM/DD/YYYY (4 January), not 1 April.
2. Parses with an explicit DD/MM/YYYY pattern (regex or a date library with a format string) and rejects invalid dates like 31/04/2026.
3. Stores or transmits dates in ISO format (YYYY-MM-DD) internally.
4. Displays with Intl.DateTimeFormat('en-IN', { day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'Asia/Kolkata' }) or equivalent, rather than relying on the browser's default time zone.

FAIL if the fix still relies on new Date(input) or Date.parse for DD/MM/YYYY strings.
