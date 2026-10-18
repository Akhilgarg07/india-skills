---
type: llm
---

PASS only if the response does ALL of the following:
1. Converts the timestamps to Indian time (AT TIME ZONE 'Asia/Kolkata' or a +05:30 offset) before deciding the financial year/quarter.
2. Uses an April-March financial year: FY start year is the year if the month is April or later, otherwise the previous year.
3. Defines quarters as Q1 Apr-Jun, Q2 Jul-Sep, Q3 Oct-Dec, Q4 Jan-Mar.
4. Explains that 23:30 UTC on 31 March is 05:00 IST on 1 April and therefore belongs to the next FY, matching finance.

FAIL if the query buckets on UTC dates or uses calendar-year quarters.
