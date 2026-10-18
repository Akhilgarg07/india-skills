# PIN circles and states: reference

## PIN structure (Department of Posts)

- Introduced 15 August 1972; 6 digits; the country is divided into **9 PIN regions**.
- 1st digit: region. First 2 digits: postal circle or sub-region. First 3 digits: sorting /
  revenue district (postal district). Last 3 digits: the delivery post office within the district.
- "The first 8 are geographical regions and the digit 9 is reserved for the Army Postal Service."
- Each PIN maps to one delivery post office (GPO, head office or sub-office) that receives mail for
  itself and the lower offices in its jurisdiction, which share the same code.

## First-digit regions (India Post circle page)

| First digit | Region |
|---|---|
| 1, 2 | Northern |
| 3, 4 | Western |
| 5, 6 | Southern |
| 7, 8 | Eastern |
| 9 | Army Postal Service (functional, not geographical) |

## First-two-digit postal circles (India Post circle page; historical names)

| First 2 digits | Circle (as published) | Today also covers (illustrative) |
|---|---|---|
| 11 | Delhi | |
| 12-13 | Haryana | |
| 14-16 | Punjab | Chandigarh (PINs 160xxx; e-invoice PIN-state mapping uses 140 and 160) |
| 17 | Himachal Pradesh | |
| 18-19 | Jammu & Kashmir | Ladakh |
| 20-28 | Uttar Pradesh | Uttarakhand |
| 30-34 | Rajasthan | |
| 36-39 | Gujarat | Dadra and Nagar Haveli and Daman and Diu `TODO(verify)` |
| 40-44 | Maharashtra | Goa `TODO(verify)` |
| 45-49 | Madhya Pradesh | Chhattisgarh |
| 50-53 | Andhra Pradesh | Telangana |
| 56-59 | Karnataka | |
| 60-64 | Tamil Nadu | Puducherry `TODO(verify)` |
| 67-69 | Kerala | Lakshadweep `TODO(verify)` |
| 70-74 | West Bengal | Sikkim, Andaman & Nicobar `TODO(verify)` |
| 75-77 | Odisha | |
| 78 | Assam | |
| 79 | North Eastern | other north-eastern states `TODO(verify)` which |
| 80-85 | Bihar | Jharkhand |
| 90-99 | Army Postal Service | |

The "Today also covers" column marks where states/UTs created or renamed after the table sit inside
the old ranges. Only the Chandigarh, Telangana, Uttarakhand, Jharkhand, Chhattisgarh and Ladakh rows
follow from the sources (Chandigarh from the IRP PIN-state mapping note; the others because those
states were carved out of the listed circle's state). Rows marked `TODO(verify)` are not confirmed.
**Do not use this table to hard-validate state.** Use the PIN directory.

## Official PIN directory

India Post publishes the **All India Pincode Directory** (office name, PIN, district, state, and
more) on the Open Government Data platform: data.gov.in "All India Pincode Directory" (CSV and
web-service). Load it into your database and refresh it periodically; PINs are added and offices
re-mapped over time.

## States and UTs: history that breaks old data

| Change | Date | Effect on data |
|---|---|---|
| J&K reorganised into UTs of J&K and Ladakh | 31 Oct 2019 | J&K is no longer a state; Ladakh (Kargil, Leh) is a separate UT (GST code 38) |
| Dadra and Nagar Haveli + Daman and Diu merged | 26 Jan 2020 | one UT, GST code 26 (code 25 was Daman and Diu until then) |
| Telangana formed | 2014 | GST code 36; Andhra Pradesh moved to 37 (28 was AP before division) |
| Orissa → Odisha, Pondicherry → Puducherry, Uttaranchal → Uttarakhand | renames | keep aliases for input matching |
