# Indian ID formats: detailed reference

Read this when you need the full state-code table, the GSTIN algorithm explained
step by step, or the reasoning behind a rule in SKILL.md. Every rule here is cited
in [sources.md](sources.md).

## GSTIN (15 characters)

CGST Rules, rule 10 (Issue of registration certificate): the GSTIN is assigned as

| Positions | Meaning |
|---|---|
| 1-2 | State code |
| 3-12 | PAN, or the Tax Deduction and Collection Account Number (TAN) |
| 13-14 | Entity code |
| 15 | Checksum character |

CBIC's registration flier adds that one PAN-based legal entity has one GSTIN per
state, so the same PAN appears in many GSTINs with different state codes.

### Entity code (positions 13-14)

The rules only say "two characters for the entity code". Position 13 is commonly
described as the count of registrations of the same PAN within a state, and
position 14 as "Z by default". **Do not enforce either.** Published, checksum-valid
GSTINs exist with `D` and `C` at position 14 (`29AABCA0522B1DP`, `27AABCA0522B1DT`,
`27AABCI2726B1CD`). Validate positions 13-14 only as `[0-9A-Z]`.

### Check character algorithm (mod 36)

GSTN has not published this algorithm in a rule or notification. The version below
reproduces the check character of all 19 real GSTINs collected from published
sources (see sources.md) and is the algorithm used across the ecosystem.
`TODO(verify): find an official GSTN/CBIC publication of the GSTIN checksum algorithm.`

1. Map each of the first 14 characters to a value: `0-9` → 0-9, `A-Z` → 10-35.
2. Multiply the value by a weight: 1 for odd positions (1st, 3rd, ...), 2 for even positions.
3. For each product, add `product // 36 + product % 36` to a running sum.
4. Check value = `(36 - sum % 36) % 36`, mapped back to `0-9A-Z`.

Worked example, `27AABCE6624L1Z` → expected `G`, so `27AABCE6624L1ZG` is valid.

### GST state codes

| Code | State / UT | Code | State / UT |
|---|---|---|---|
| 01 | Jammu and Kashmir | 20 | Jharkhand |
| 02 | Himachal Pradesh | 21 | Odisha |
| 03 | Punjab | 22 | Chhattisgarh |
| 04 | Chandigarh | 23 | Madhya Pradesh |
| 05 | Uttarakhand | 24 | Gujarat |
| 06 | Haryana | 25 | Daman and Diu (July 2017 to 26 Jan 2020 only) |
| 07 | Delhi | 26 | Dadra and Nagar Haveli and Daman and Diu |
| 08 | Rajasthan | 27 | Maharashtra |
| 09 | Uttar Pradesh | 28 | Andhra Pradesh (before division; historical) |
| 10 | Bihar | 29 | Karnataka |
| 11 | Sikkim | 30 | Goa |
| 12 | Arunachal Pradesh | 31 | Lakshadweep |
| 13 | Nagaland | 32 | Kerala |
| 14 | Manipur | 33 | Tamil Nadu |
| 15 | Mizoram | 34 | Puducherry |
| 16 | Tripura | 35 | Andaman and Nicobar Islands |
| 17 | Meghalaya | 36 | Telangana |
| 18 | Assam | 37 | Andhra Pradesh |
| 19 | West Bengal | 38 | Ladakh |
| 97 | Other Territory | 99 | `TODO(verify):` sources disagree on the label ("Centre Jurisdiction" vs "Other Country") |

Notes:
- Code **26** is the merged UT (since 26 Jan 2020). Code 25 was Daman and Diu before the merger.
- Code **38** (Ladakh) and **37** (Andhra Pradesh) are newer codes; old code lists
  copied from blogs often miss them.
- Codes are two digits with a leading zero. Store them as strings (`"07"`, not `7`).

## PAN (10 characters)

Income Tax Department, "How PAN is formed" (example `ALWPG5809L`):

| Positions | Meaning |
|---|---|
| 1-3 | Alphabetic series AAA to ZZZ |
| 4 | Status of PAN holder |
| 5 | First letter of surname (individual) / of name (non-individual) |
| 6-9 | Sequential number 0001 to 9999 |
| 10 | Alphabetic check digit (algorithm not public, so cannot be verified) |

Status codes: `A` Association of Persons, `B` Body of Individuals, `C` Company,
`F` Firm / LLP, `G` Government Agency, `H` HUF, `J` Artificial Juridical Person,
`L` Local Authority, `P` Individual, `T` Trust.

## TAN (10 characters)

Income Tax Department, "What is TAN?" (example `DELM12345L`): first 3 letters are the
jurisdiction code, 4th letter is the initial of the TAN holder's name, positions 5-9
are digits 00001 to 99999, position 10 is an alphabetic check digit.

## IFSC (11 characters)

RBI NEFT FAQ: first 4 alphabetic characters = bank, 5th character = `0` (zero),
last 6 characters = branch. RBI's IFSC committee report describes the 5th position as
"numeric (kept 0)" and reserved for future use. RBI's own IFSC `RBIS0NDPA01` shows that
the branch part can contain letters.

## Mobile numbers

- DoT National Numbering Plan 2003: the National Significant Number is 10 digits for
  basic and cellular mobile services. Country code +91.
- TRAI (29 May 2020): mobile numbers are allocated from level 9, sub-levels of 7 and 8,
  and a few sub-levels of 6. A first digit of 6-9 is therefore necessary but not
  sufficient; some 6xx/7xx/8xx ranges are fixed-line.
- Mobile number portability (since 2015) means the prefix no longer identifies the operator
  or circle.

## PIN code

Department of Posts (PIB release): 6 digits, 9 PIN regions; the first 8 are
geographical and 9 is the Army Postal Service. First 2 digits = sub-region / postal
circle; first 3 = sorting / revenue district; last 3 = delivery post office.
Region-to-state mapping lives in the `indian-addresses` skill.

## Aadhaar

12 digits; last digit is a Verhoeff check digit (UIDAI API 2.0 error-handling
guide, error 998: "Aadhaar number should be 12 digits and conform to Verhoeff
algorithm"). The number is random and encodes no personal data. Handling
rules: [aadhaar-handling.md](aadhaar-handling.md).
