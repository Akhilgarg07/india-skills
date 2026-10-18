---
name: indian-addresses
description: Design and validate Indian address forms and data correctly - field structure (house/flat, building, street, locality, landmark, city/town/village, district, state, PIN code), the official list of 28 States and 8 Union Territories with GST state codes, old-name aliases (Orissa, Pondicherry, Uttaranchal), PIN code structure and what a PIN prefix can and cannot tell you, DIGIPIN, and common pitfalls in checkout, KYC, delivery and CRM systems. Use when building address forms, state dropdowns, PIN-code autofill, address validation or normalisation, or shipping/serviceability logic for India. Includes a stdlib Python states/UTs and PIN-prefix helper.
license: MIT
metadata:
  version: "0.1.0"
  last-verified: "2026-10-18"
---

# Indian addresses

## Recommended form fields

| Field | Required? | Notes |
|---|---|---|
| Full name | yes | single field; don't force first/last name (many people have one name) |
| Mobile | yes for delivery | 10 digits, store E.164 `+91…` (see `indian-id-validation`) |
| PIN code | **yes** | 6 digits, first digit 1-9; ask for it **first** and use it to suggest city/district/state |
| Address line 1 | yes | house/flat/plot no., building/society/apartment name |
| Address line 2 | optional | street/road, area/locality/sector/colony |
| Landmark | optional, but **include it** | "Near Hanuman Temple": widely used by couriers in India |
| City / Town / Village | yes | free text; pre-fill from PIN but keep editable |
| District | optional | useful for KYC and government forms |
| State / UT | yes | dropdown of all **28 States + 8 UTs** |
| Country | fixed "India" | or hidden |

Design rules:
- **Don't require a street name or house number format.** Many valid addresses are
  "Near X, Y village", "C/o Ramesh Kumar", plot/khasra numbers, or sector/block addresses.
- Allow **long lines** (at least 100-150 chars each) and Unicode; people write addresses in English and
  Indian scripts. Don't strip `/`, `-`, `#`, `,`, `.` or `(`.
- One PIN code covers many localities, and the same locality name exists in many states. **PIN
  lookups suggest; they never overwrite** what the user typed.
- Validate the **format** of the PIN code strictly. Treat PIN ↔ state mismatches as **warnings**
  ("This PIN looks like it belongs to Punjab postal circle, are you sure?"), not hard errors,
  unless you check against the official PIN directory.
- Store the PIN as a **string**; store the state as a canonical name **plus** a code (2-digit GST state
  code works well and is needed for GST invoices anyway).
- Delivery serviceability is courier-specific; check it against your logistics partner's PIN list, not
  the India Post directory.

## States and Union Territories (MHA; GST state code)

**States (28):** Andhra Pradesh 37, Arunachal Pradesh 12, Assam 18, Bihar 10, Chhattisgarh 22,
Goa 30, Gujarat 24, Haryana 06, Himachal Pradesh 02, Jharkhand 20, Karnataka 29, Kerala 32,
Madhya Pradesh 23, Maharashtra 27, Manipur 14, Meghalaya 17, Mizoram 15, Nagaland 13, Odisha 21,
Punjab 03, Rajasthan 08, Sikkim 11, Tamil Nadu 33, Telangana 36, Tripura 16, Uttar Pradesh 09,
Uttarakhand 05, West Bengal 19.

**Union Territories (8):** Andaman and Nicobar Islands 35, Chandigarh 04, Dadra and Nagar Haveli and
Daman and Diu 26, Delhi 07 (NCT, has legislature), Jammu and Kashmir 01 (has legislature), Ladakh 38,
Lakshadweep 31, Puducherry 34 (has legislature).

Pitfalls:
- Old lists still have **29 states / 7 UTs** (before J&K was reorganised on 31 Oct 2019) or list Daman
  and Diu and Dadra and Nagar Haveli separately (merged in Jan 2020). Remove "Jammu and Kashmir (state)".
- Use current names: **Odisha** (not Orissa), **Puducherry** (not Pondicherry), **Uttarakhand** (not
  Uttaranchal). Accept the old names as input aliases and map them.
- Telangana and Andhra Pradesh are separate (Telangana GST code 36, AP 37).
- Don't label the dropdown "State" only; use **"State / UT"**.

## PIN codes: what a prefix tells you

- 6 digits, introduced in 1972. **9 PIN regions**: the first digit is the region (1-8 geographical,
  **9 = Army Postal Service**); the first 2 digits are the **postal circle / sub-region**; the first 3 are
  the **sorting district**; the last 3 are the **delivery post office**.
- Region by first digit: 1-2 Northern, 3-4 Western, 5-6 Southern, 7-8 Eastern, 9 APS.
- A postal circle is **not a state**. Circle ranges in India Post's table predate several
  states (Telangana PINs sit in the "Andhra Pradesh" 50-53 range; Uttarakhand in the 20-28 "Uttar
  Pradesh" range; Jharkhand in the 80-85 "Bihar" range), and UTs share neighbouring circles
  (Chandigarh PINs start 160, inside the Punjab 14-16 range). Full table:
  [references/pin-and-states.md](references/pin-and-states.md).
- **For PIN → district/state, use the All India Pincode Directory** (India Post data on
  data.gov.in), refreshed periodically, not prefix arithmetic.

## DIGIPIN

India Post's **DIGIPIN** is a 10-character alphanumeric geo-code for a roughly 4 m × 4 m grid cell,
derived from latitude/longitude. It **complements** the PIN code (which identifies a delivery post
office area) and doesn't replace it. Accept it as an optional field if your delivery partners support it.

## Script

```bash
python3 scripts/india_regions.py list               # all 36 with GST codes
python3 scripts/india_regions.py state "Orissa"     # -> Odisha (21)
python3 scripts/india_regions.py pin 560001         # region Southern, circle Karnataka
```
Module: `STATES_AND_UTS`, `find_state(name_or_alias_or_gst_code)` (returns `None` when unknown or
ambiguous, e.g. "UK"), `pin_info(pin)`. PIN format validation itself is in the
`indian-id-validation` skill.

Address JSON shape, normalisation tips and more pitfalls:
[references/address-design.md](references/address-design.md). Sources: [references/sources.md](references/sources.md).
