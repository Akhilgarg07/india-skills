---
name: indian-number-formatting
description: Format numbers and money the Indian way - lakh/crore digit grouping (1,00,000 and 1,00,00,000), the ₹ symbol (U+20B9), Intl.NumberFormat('en-IN') usage and its pitfalls (compact notation, long display, missing ICU data), parsing Indian-formatted input, lakh/crore short forms, and amount in words in Indian English ("One Lakh Twenty Thousand Rupees Only"). Use when displaying prices, invoices, cheques, reports or dashboards for Indian users, writing currency formatters, converting amounts to words, or parsing amounts typed by Indian users. Includes stdlib Python formatter and amount-in-words scripts.
license: MIT
metadata:
  version: "0.1.0"
  last-verified: "2026-10-18"
---

# Indian number formatting

## Grouping: lakh and crore

| Value | Indian grouping | Words | International |
|---|---|---|---|
| 1,000 | 1,000 | one thousand | 1,000 |
| 1,00,000 | 1,00,000 | **one lakh** | 100,000 |
| 10,00,000 | 10,00,000 | ten lakh | 1,000,000 (1 million) |
| 1,00,00,000 | 1,00,00,000 | **one crore** | 10,000,000 |
| 1,00,00,00,000 | 1,00,00,00,000 | one hundred crore | 1,000,000,000 (1 billion) |
| 10,00,00,00,00,000 | 10,00,00,00,00,000 | one lakh crore | 1,000,000,000,000 (1 trillion) |

Rule: the **last three** integer digits form one group; every group to the left has **two**
digits (CLDR `en-IN` pattern `#,##,##0.###`; currency `¤#,##,##0.00`). Decimals are not grouped.

## JavaScript: `Intl.NumberFormat("en-IN")`

```js
new Intl.NumberFormat("en-IN").format(1234567.891);                          // "12,34,567.891"
new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(1234567.5);
                                                                             // "₹12,34,567.50"
new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR",
                                 maximumFractionDigits: 0 }).format(120000); // "₹1,20,000"
new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(-1500); // "-₹1,500.00"
(1234567).toLocaleString("en-IN");                                           // "12,34,567"
```

Pitfalls (verified on Node 22 with full ICU):
- **Always pass the locale.** `toLocaleString()` with no locale uses the runtime default (often
  `en-US` on servers, giving `1,234,567`).
- `notation: "compact"` gives `"13L"` for 12,50,000: it **rounds to 2 significant digits** by
  default, and `compactDisplay: "long"` gives **"1.3 million"**, not lakh. For "12.5 lakh", format
  it yourself (see `short_lakh_crore`) or set `maximumFractionDigits`.
- Runtimes without full ICU data (some embedded or old mobile JS engines, `small-icu` builds) may
  silently fall back to `en-US` grouping. Test on the target runtime, or ship a formatter.
- Format from **integer paise / decimal strings**, not floats, when exact paise matter.
  `Intl.NumberFormat` also accepts strings and BigInt.
- `currencyDisplay: "code"` gives `"INR 100.00"`; `"symbol"` (default) gives `₹`.
- `hi-IN` uses the same grouping (`₹12,34,567.50` with Latin digits by default).
- Python's `locale` module depends on OS locales (often missing in containers); `format(n, ",")`
  is international grouping. Use the script below or Babel.

## The ₹ symbol

- Unicode **U+20B9 INDIAN RUPEE SIGN** (`₹`, HTML `&#8377;`), approved by the Union Cabinet on
  15 July 2010. Use the character, not an image or the old `Rs.` font hack.
- Put it before the number with **no space** (`₹1,20,000`), as `en-IN` formatting does. A negative
  is `-₹1,500.00`.
- Ensure your font has the glyph (most system fonts since about 2012 do); embed a fallback in PDF
  generators (e.g. Noto Sans) or the symbol renders as a box.
- In plain-text contexts where ₹ may not survive (SMS, legacy systems), use `Rs.` or `INR`.

## Parsing Indian-formatted input
Users type `1,20,000`, `120000`, `₹ 1,20,000`, `Rs. 1,20,000/-`, `1.2 lakh`. Strip `₹`, `Rs`,
`INR`, `/-` and commas, then parse as a decimal. Don't validate comma positions (users mix
styles). Don't silently interpret "1.2 lakh"; either support "lakh"/"crore" words explicitly or
reject them.

## Amount in words (Indian English)

Common invoice/cheque convention: Title Case, lakh/crore units, ending with **"Only"**:
- `120000` → **One Lakh Twenty Thousand Rupees Only** (or prefix style: *Rupees One Lakh Twenty
  Thousand Only*)
- `1050.50` → One Thousand Fifty Rupees and Fifty Paise Only
- `1` → One Rupee Only; `0.01` → One Paisa Only
- `12,34,56,789` → Twelve Crore Thirty Four Lakh Fifty Six Thousand Seven Hundred Eighty Nine Rupees Only
- `10^12` → One Lakh Crore Rupees Only (not "One Trillion")

Rules: use lakh and crore, never million/billion; write "Twelve Lakh", "Five Crore" (the usual
formal style; avoid "Lakhs"/"Crores"); round to paise first; `and` inside hundreds ("One Hundred and
Five") is a house-style choice, so pick one and be consistent. Words must match the figures exactly.

## Scripts (Python 3, standard library only)

```bash
python3 scripts/inr_format.py 1234567.5               # ₹12,34,567.50
python3 scripts/inr_format.py 120000 --decimals 0     # ₹1,20,000
python3 scripts/inr_format.py 1250000 --short         # 12.5 lakh
python3 scripts/inr_format.py "Rs. 1,20,000/-" --parse  # 120000
python3 scripts/amount_in_words.py 120000             # One Lakh Twenty Thousand Rupees Only
python3 scripts/amount_in_words.py 1050.50 --prefix   # Rupees One Thousand Fifty and Fifty Paise Only
```
Module: `group_indian`, `format_indian`, `format_inr`, `parse_indian`, `short_lakh_crore`;
`number_to_words`, `amount_in_words(amount, style=, use_and=, only=)`.

More examples and other-language notes: [references/formatting-reference.md](references/formatting-reference.md).
Sources: [references/sources.md](references/sources.md).
