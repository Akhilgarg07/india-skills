# Indian number formatting: extra reference

## Observed `Intl.NumberFormat` output (Node 22.22, full ICU)

| Code | Output |
|---|---|
| `new Intl.NumberFormat("en-IN").format(1234567.891)` | `12,34,567.891` |
| `...("en-IN", {style:"currency", currency:"INR"}).format(1234567.5)` | `₹12,34,567.50` |
| `...({style:"currency", currency:"INR", maximumFractionDigits:0}).format(120000)` | `₹1,20,000` |
| `...({style:"currency", currency:"INR"}).format(-1500)` | `-₹1,500.00` |
| `...({style:"currency", currency:"INR", currencyDisplay:"code"}).format(100)` | `INR 100.00` |
| `...({notation:"compact"}).format(1250000)` | `13L` (rounded!) |
| `...({notation:"compact", maximumFractionDigits:1}).format(1250000)` | `12.5L` |
| `...({notation:"compact", compactDisplay:"long"}).format(1250000)` | `1.3 million` (not lakh) |
| `...({notation:"compact"}).format(25000000)` | `2.5Cr` |
| `...({style:"currency", currency:"INR"}).format("12345678901234567.89")` | `₹12,34,56,78,90,12,34,567.89` (string input keeps precision) |
| `...({style:"currency", currency:"INR"}).format(10n ** 12n)` | `₹10,00,00,00,00,000.00` |
| `new Intl.NumberFormat("hi-IN", {style:"currency", currency:"INR"}).format(1234567.5)` | `₹12,34,567.50` |

Beyond a crore, CLDR keeps grouping in twos (`1,23,45,67,89,01,234`). Large figures are usually
spoken as "lakh crore" (e.g. ₹63 lakh crore).

## Other environments

- **Java:** `NumberFormat.getCurrencyInstance(Locale.forLanguageTag("en-IN"))` (CLDR data, JDK 9+).
- **Python:** `babel.numbers.format_currency(1234567.5, "INR", locale="en_IN")` →
  `₹12,34,567.50` (third-party), or this skill's `inr_format.py` (stdlib).
- **PostgreSQL:** `to_char` has no lakh grouping; format in the application layer.
- **Excel / Google Sheets:** set the cell/sheet locale to English (India) where supported, then use a
  number format; check the result, because support varies by product and version.
- **Android:** `NumberFormat.getCurrencyInstance(Locale("en", "IN"))`.

## Amount-in-words conventions

- Units: Thousand (10^3), Lakh (10^5), Crore (10^7). Above 99 crore, continue with the crore count
  in words: "One Hundred Crore", "One Thousand Crore", "One Lakh Crore".
- Typical invoice line: `Amount in words: One Lakh Eighteen Thousand Rupees Only`.
- Cheque style (prefix): `Rupees One Lakh Eighteen Thousand Only`.
- Paise: "... Rupees and Fifty Paise Only"; singular "One Rupee", "One Paisa".
- Hyphenation ("Twenty-One") and "and" between hundreds and tens are style choices. Pick one per
  product; the scripts default to no hyphen and no "and".
- Generate words from the **same rounded decimal** used for the figure, never from a float.

## Indian languages
For words in Hindi or other Indian languages, use a localisation library or a reviewed lookup
table; the numbers 1-99 are irregular in most Indian languages, so you cannot compose them from
"tens + ones" the way English does.
