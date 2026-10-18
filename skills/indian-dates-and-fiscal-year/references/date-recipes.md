# Date recipes for Indian FY and IST

## Python
```python
import datetime as dt
from zoneinfo import ZoneInfo
IST = ZoneInfo("Asia/Kolkata")

def fy_start_year(d: dt.date) -> int:
    return d.year if d.month >= 4 else d.year - 1

def fy_label(d: dt.date) -> str:
    s = fy_start_year(d)
    return f"{s}-{(s + 1) % 100:02d}"

ts = dt.datetime(2026, 3, 31, 20, 15, tzinfo=dt.timezone.utc)
fy_label(ts.astimezone(IST).date())          # '2026-27'  (it is already 1 Apr in India)
dt.datetime.strptime("01/04/2026", "%d/%m/%Y").date()   # strict DD/MM/YYYY
```

## JavaScript / TypeScript
```ts
const IST = "Asia/Kolkata";
// Calendar parts in IST without libraries
function istParts(d: Date) {
  const p = Object.fromEntries(new Intl.DateTimeFormat("en-CA", {
    timeZone: IST, year: "numeric", month: "2-digit", day: "2-digit",
  }).formatToParts(d).map(x => [x.type, x.value]));
  return { y: +p.year, m: +p.month, d: +p.day };
}
function fyLabel(d: Date) {
  const { y, m } = istParts(d);
  const s = m >= 4 ? y : y - 1;
  return `${s}-${String((s + 1) % 100).padStart(2, "0")}`;
}
// Strict DD/MM/YYYY parse (never new Date("01/04/2026"), which is 4 January)
function parseDDMMYYYY(s: string) {
  const m = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(s.trim());
  if (!m) throw new Error("expected DD/MM/YYYY");
  const [_, dd, mm, yyyy] = m;
  const d = new Date(Date.UTC(+yyyy, +mm - 1, +dd));
  if (d.getUTCMonth() !== +mm - 1 || d.getUTCDate() !== +dd) throw new Error("invalid date");
  return `${yyyy}-${mm}-${dd}`;                          // ISO date string
}
```
`Temporal` (where available) and libraries like `date-fns-tz` / Luxon handle zones well. Always pass
`Asia/Kolkata` explicitly.

## SQL
```sql
-- PostgreSQL: FY start year of a timestamptz, bucketed in IST
SELECT CASE WHEN EXTRACT(MONTH FROM ts AT TIME ZONE 'Asia/Kolkata') >= 4
            THEN EXTRACT(YEAR FROM ts AT TIME ZONE 'Asia/Kolkata')
            ELSE EXTRACT(YEAR FROM ts AT TIME ZONE 'Asia/Kolkata') - 1 END AS fy_start
FROM payments;

-- FY quarter (1-4)
SELECT ((EXTRACT(MONTH FROM ts AT TIME ZONE 'Asia/Kolkata')::int + 8) % 12) / 3 + 1 AS fy_quarter
FROM payments;
```
(For April, `(4 + 8) % 12 = 0`, so `0 / 3 + 1 = 1`; for March, `(3 + 8) % 12 = 11`, so `11 / 3 + 1 = 4`.)

## Cron / schedulers
| IST | UTC |
|---|---|
| 00:00 | 18:30 previous day |
| 09:00 | 03:30 |
| 18:00 | 12:30 |
| 23:59 | 18:29 |

"Run at midnight India time" = `30 18 * * *` in UTC cron. Better: set the scheduler's timezone to
`Asia/Kolkata` if it supports it.

## FY-end gotchas
- 31 March is a busy cut-off (tax-saving investments, TDS, books closing). Batch jobs that run "for
  yesterday" at 00:30 IST on 1 April must use the previous FY.
- Leap years: FY 2027-28 includes 29 Feb 2028. Don't assume 365 days.
- Labels like "FY26" are ambiguous between teams (some mean 2025-26, some 2026-27). Prefer `2025-26`.
