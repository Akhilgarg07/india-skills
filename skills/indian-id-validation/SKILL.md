---
name: indian-id-validation
description: Validate Indian identifiers correctly - GSTIN (with its mod-36 check character), PAN, TAN, IFSC, Indian mobile numbers, PIN codes and Aadhaar (format + Verhoeff checksum only, always masked). Use when writing or reviewing form validation, KYC/onboarding flows, invoice or vendor-master imports, regexes, database constraints, or test data that involve any of these IDs, or when a user asks whether such a number "looks valid". Includes stdlib Python validators and strict rules for never storing, logging or displaying full Aadhaar numbers.
license: MIT
metadata:
  version: "0.1.0"
  last-verified: "2026-10-18"
---

# Indian ID validation

Validate the **format and checksum** of Indian identifiers. Never claim that a
format check proves an ID exists, is active, or belongs to the user.

> Not legal advice. Aadhaar handling is regulated (Aadhaar Act 2016 and UIDAI
> regulations); rules change. Check the current UIDAI regulations for your use case.

## Quick reference

| ID | Length | Format check | Checksum |
|---|---|---|---|
| GSTIN | 15 | `^[0-9]{2}[0-9A-Z]{13}$`, valid state code, chars 3-12 = PAN (or TAN) | Mod-36 check character, **always verify** |
| PAN | 10 | `^[A-Z]{3}[ABCFGHJLPT][A-Z][0-9]{4}[A-Z]$` | Exists, but algorithm not published, so skip |
| TAN | 10 | `^[A-Z]{4}[0-9]{5}[A-Z]$` | Not published, so skip |
| IFSC | 11 | `^[A-Z]{4}0[A-Z0-9]{6}$` (5th char is digit zero) | None |
| Mobile | 10 | `^[6-9][0-9]{9}$` after stripping `+91` / `91` / `0` | None |
| PIN code | 6 | `^[1-9][0-9]{5}$` | None |
| Aadhaar | 12 | 12 digits | Verhoeff, **always verify**, then mask |

Details, state codes and the GSTIN algorithm: [references/id-formats.md](references/id-formats.md).
Aadhaar storage and display rules: [references/aadhaar-handling.md](references/aadhaar-handling.md).

## Scripts (Python 3, standard library only)

Each works as a CLI and as an importable module (`validate()` returns a dict with
`valid`, `errors`, and parsed fields). Exit code 0 = all valid, 1 = any invalid.

```bash
python3 scripts/gstin_validate.py 27AABCE6624L1ZG      # state, PAN, check char
python3 scripts/pan_validate.py ALWPG5809L             # holder type
python3 scripts/pan_validate.py --tan DELM12345L
python3 scripts/ifsc_validate.py RBIS0NDPA01
python3 scripts/mobile_validate.py "+91 98765 43210"   # -> +919876543210
python3 scripts/pincode_validate.py 110001
printf '%s' "$NUM" | python3 scripts/aadhaar_validate.py   # stdin only, prints masked
python3 scripts/verhoeff.py digit 236                  # -> 3
```

Use `--json` for machine-readable output. Run the scripts to check sample data or
to confirm an algorithm port; port the logic into the user's language for production.

## Rules

### General
1. **Format-valid is not verified.** Say "valid format" in UI copy and code names
   (`isValidGstinFormat`, not `isRealGstin`). Existence needs an authoritative
   lookup: GST portal *Search Taxpayer* / a GSP API for GSTIN, an authorised PAN
   verification service, RBI's IFSC list, an OTP for mobile ownership, India Post's
   PIN directory.
2. **Normalise, don't autocorrect.** Trim and uppercase GSTIN/PAN/TAN/IFSC. Strip
   spaces/hyphens from phone and Aadhaar input. Never silently change characters
   (e.g. letter `O` to digit `0` in an IFSC); show a hint and let the user fix it.
3. **Store the normalised form** (uppercase, no spaces; phones in E.164 `+91XXXXXXXXXX`).
4. Give **specific error messages** ("check character should be 'G'") rather than "invalid".

### GSTIN
- Always verify the **check character**; a regex alone accepts most typos.
- Do **not** hard-code `Z` as the 14th character. Real GSTINs have other letters
  there (`29AABCA0522B1DP`, `27AABCI2726B1CD` both pass the check character).
- The state code must be a GST state code (01-38, 97, 99); see the table in
  references. Codes 25 and 28 are historical.
- Characters 3-12 are the PAN for normal taxpayers, but the **TAN** for tax-deductor
  registrations, and a different pattern for UIN / some non-resident registrations.
  If you require a PAN there, you will reject legitimate GSTINs, so decide explicitly.
- Same PAN + different state code = different registrations of one legal entity.
  Never treat GSTIN as unique per company.

### PAN
- 4th character = holder status: `P` Individual, `C` Company, `H` HUF, `F` Firm/LLP,
  `A` AOP, `B` BOI, `T` Trust, `G` Government agency, `J` Artificial juridical person,
  `L` Local authority. Reject other letters.
- 5th character = first letter of the surname (individuals) or name (others). Use it
  at most as a soft warning; name formats vary too much to hard-reject.
- Treat PAN as personal data: mask in logs (`ALWPG****L`), restrict access.

### IFSC
- 5th character is the **digit** zero. First 4 = bank, last 6 = branch (alphanumeric).
- Do not derive bank names from the 4-letter prefix by hard-coded list; use the RBI dataset.

### Mobile
- Accept `+91`, `0091`, `91` (12 digits) or a leading `0`, then require 10 digits
  starting 6-9. Store E.164. Don't infer operator or state from the prefix
  (mobile number portability).
- For `<input>`, use `type="tel"` with `inputmode="numeric"`, not `type="number"`.

### PIN code
- 6 digits, first digit 1-9 (9 = Army Postal Service). Accept `560 001` but store `560001`.
- Store PIN codes as **strings**, never integers.

### Aadhaar (strict)
Read [references/aadhaar-handling.md](references/aadhaar-handling.md) before writing any code that touches Aadhaar.
- Validate only **12 digits + Verhoeff checksum**. Don't add other "rules" (e.g.
  first-digit restrictions) unless the user cites a UIDAI source.
- **Never log, print, return in API errors, send to analytics, or put in URLs** the
  full number. Mask as `XXXX XXXX 1234` (last four digits only) everywhere it is displayed.
- **Never store** the full number unless the user's organisation is permitted to and
  uses a separate encrypted **Aadhaar Data Vault** with reference keys. Otherwise
  store at most the masked form or a reference token.
- Never put real Aadhaar numbers in test fixtures. Generate synthetic ones with
  `verhoeff.check_digit()`. UIDAI's own sandbox test number (`999999990019`) does
  **not** pass Verhoeff, so give sandbox/test mode a way to skip the checksum.
- A valid checksum is not identity verification. Identity needs UIDAI authentication
  (through a licensed AUA/KUA) or offline verification; don't build your own.

## Code snippets

GSTIN check character (JavaScript):
```js
const A = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
export function gstinCheckChar(first14) {
  let sum = 0;
  for (let i = 0; i < 14; i++) {
    const p = A.indexOf(first14[i]) * (i % 2 ? 2 : 1);
    sum += Math.floor(p / 36) + (p % 36);
  }
  return A[(36 - (sum % 36)) % 36];
}
export const isValidGstinFormat = (g) =>
  /^[0-9]{2}[0-9A-Z]{13}$/.test(g) && gstinCheckChar(g.slice(0, 14)) === g[14];
// Also check g.slice(0, 2) against the state-code table.
```

Aadhaar masking (any language): keep `digits.slice(-4)`, prefix `"XXXX XXXX "`.
Mask **before** the value reaches any logger, error tracker or response body.

## Test values

Use these (published or synthetic, never personal data):
- GSTIN valid: `27AABCE6624L1ZG`, `07AABCE6624L1ZI`, `29AABCI2726B1ZY`, `29AABCA0522B1DP`.
  Invalid: `27AABCE6624L1ZH` (bad check char), `40AABCE6624L1ZG` (bad state code).
- PAN valid: `ALWPG5809L` (Income Tax Department's example). Invalid: `ALWXG5809L` (4th char).
- IFSC valid: `RBIS0NDPA01`. Invalid: `RBISONDPA01` (letter O in 5th position).
- Aadhaar: synthetic only, e.g. `23412341234` + `verhoeff.check_digit("23412341234")`.
