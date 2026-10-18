---
name: indian-dates-and-fiscal-year
description: Handle Indian dates and the financial year correctly - the April-March financial year (FY 2026-27 labels, quarters Q1 = Apr-Jun), assessment year vs the new "tax year" under the Income-tax Act 2025 (from 1 April 2026), IST (UTC+05:30, no daylight saving, Asia/Kolkata), DD/MM/YYYY display and strict parsing, and Intl/locale pitfalls with en-IN. Use when writing reports, dashboards, invoice numbering, accounting periods, payroll or tax logic, date pickers, cron/schedulers, or any code that buckets dates into Indian FYs or converts timestamps to Indian time. Includes a stdlib Python FY/IST helper.
license: MIT
metadata:
  version: "0.1.0"
  last-verified: "2026-10-18"
---

# Indian dates and the financial year

> **Not tax advice.** Assessment/tax-year rules come from the Income-tax Acts and change with
> Union Budgets. The date mechanics below are stable; the tax labels are verified as of the
> last-verified date.

## Financial year (FY)

- Runs **1 April to 31 March** (General Clauses Act, 1897: "the year commencing on the first day of
  April"). Used by Government budgets, GST, income tax, and company accounts (Companies Act 2013
  s.2(41): period ending 31 March, with limited exceptions such as subsidiaries of foreign companies
  with Central Government approval).
- **Label:** `FY 2026-27` = 1 Apr 2026 to 31 Mar 2027. Some teams write `FY27`; spell out `2026-27` in
  documents and data. Compute `"%d-%02d" % (start, (start + 1) % 100)` so 1999 gives `1999-00`.
- **Start year:** `year if month >= 4 else year - 1`. 31 Mar 2026 belongs to FY 2025-26; 1 Apr 2026
  belongs to FY 2026-27.
- **Quarters:** Q1 Apr-Jun, Q2 Jul-Sep, Q3 Oct-Dec, **Q4 Jan-Mar** (calendar year + 1).
  Month 1 of the FY is April.
- Bucket a **timestamp** into an FY **after converting to IST**. 31 Mar 2026 20:15 UTC is
  1 Apr 2026 01:45 IST, which falls in the next FY.
- GST invoice numbers must be unique per FY, so include the FY in the series
  (`INV/2026-27/0001`) and reset counters on 1 April (see `gst-invoicing`).

## Assessment year vs tax year (income tax)

| Income earned in | Act | Term used | Example |
|---|---|---|---|
| FY up to 2025-26 | Income-tax Act 1961 | **previous year** (PY) assessed in the **assessment year** (AY) = FY + 1 | FY 2025-26 → **AY 2026-27** |
| FY 2026-27 onwards | Income-tax Act 2025 (in force 1 Apr 2026) | **tax year** = the FY itself; no separate AY | FY 2026-27 → **Tax Year 2026-27** |

- Returns for FY 2025-26 income are still filed for **AY 2026-27 under the 1961 Act**, even though
  they are filed after 1 April 2026. Don't relabel them "Tax Year".
- A user selecting "2026-27" is **ambiguous** (AY 2026-27 = FY 2025-26 income, but Tax Year 2026-27 =
  FY 2026-27 income). In UIs, always show which one and the income period.
- TDS credits: deductions up to Mar 2026 → AY 2026-27 (AIS); from Apr 2026 → Tax Year 2026-27
  (Form 168). See `tds-basics`.

## IST (Indian Standard Time)

- **UTC+05:30**, one zone for the whole country, **no daylight saving**. Maintained by CSIR-NPL.
- IANA zone: **`Asia/Kolkata`** (`Asia/Calcutta` is a legacy alias). Historical note: the tz database
  records +06:30 war time in 1942-45, so use the zone, not a fixed offset, for historical timestamps.
- Store timestamps in **UTC** (or with an offset); convert to IST for display, for FY/day bucketing
  and for "end of day" business rules. Cron on UTC servers: 09:00 IST = 03:30 UTC.
- Never assume the server or browser timezone is IST. Pass `timeZone: "Asia/Kolkata"` explicitly.
- Display `IST` or `+05:30`; avoid ambiguous zone abbreviations elsewhere in the UI.

## DD/MM/YYYY

- Indian convention is **day-month-year**: `01/04/2026` = 1 April 2026. Also common: `01-04-2026`,
  `1 Apr 2026`. GST e-invoice JSON uses `DD/MM/YYYY` for document dates.
- **Parse strictly.** Never let a library guess MM/DD (JavaScript `new Date("01/04/2026")` gives
  **4 January**). Use an explicit format (`dd/MM/yyyy`) or ISO `YYYY-MM-DD` internally.
- For APIs and storage use ISO 8601 (`2026-04-01`, `2026-04-01T01:45:00+05:30`).
- In forms, prefer a date picker, or three labelled fields (Day / Month / Year) rather than a free
  text box.

### `Intl.DateTimeFormat("en-IN")` pitfalls (observed, Node 22)
```js
const d = new Date(Date.UTC(2026, 2, 31, 20, 15));                // 31 Mar 2026 20:15 UTC
const f = (o) => new Intl.DateTimeFormat("en-IN", { timeZone: "Asia/Kolkata", ...o }).format(d);
f({})                                   // "1/4/2026"     (no zero padding)
f({ dateStyle: "short" })               // "01/04/26"     (two-digit year)
f({ day: "2-digit", month: "2-digit", year: "numeric" })   // "01/04/2026"  ← DD/MM/YYYY
f({ dateStyle: "medium" })              // "1 Apr 2026"
f({ timeStyle: "short" })               // "1:45 am"  (U+202F narrow no-break space, lowercase am)
```
- Times use a **narrow no-break space (U+202F)** before `am`/`pm`. Don't string-compare or regex
  on formatted output, and don't parse it back.
- Without `timeZone`, output uses the runtime's zone (often UTC on servers): the date can be off by one.

## Script

```bash
python3 scripts/fiscal_year.py fy 2026-03-31     # FY 2025-26, Q4, AY 2026-27 (1961 Act)
python3 scripts/fiscal_year.py fy 01/04/2026     # FY 2026-27, Q1, Tax Year 2026-27 (2025 Act)
python3 scripts/fiscal_year.py ist 2026-03-31T20:15:00Z   # 2026-04-01T01:45:00+05:30
```
Module: `financial_year(date)`, `fy_start_year`, `fy_label`, `quarter_range(start_year, q)`,
`parse_ddmmyyyy` (strict), `parse_date`, `format_ddmmyyyy`, `to_ist` (rejects naive datetimes).

More examples (SQL, JS, Python snippets): [references/date-recipes.md](references/date-recipes.md).
Sources: [references/sources.md](references/sources.md).
