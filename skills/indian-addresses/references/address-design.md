# Address data design for India

## Suggested JSON shape

```json
{
  "name": "Priya Sharma",
  "phone": "+919876543210",
  "line1": "Flat 302, Shanti Apartments",
  "line2": "12th Main Road, HSR Layout Sector 6",
  "landmark": "Near Agara Lake",
  "city": "Bengaluru",
  "district": "Bengaluru Urban",
  "state": "Karnataka",
  "state_code": "29",
  "pin": "560102",
  "country": "IN",
  "digipin": null
}
```

- `state_code` = 2-digit GST state code (string, keep the leading zero).
- `pin` is a string. Never an integer column (leading-zero bugs don't apply to PINs, which start 1-9,
  but integer columns invite arithmetic and lose formatting rules).
- Keep the user's original text; store normalised values alongside if you need them for matching.

## Normalisation that is safe
- Trim whitespace, collapse repeated spaces, normalise Unicode (NFC).
- Map state aliases (Orissa → Odisha, Pondicherry → Puducherry, Uttaranchal → Uttarakhand,
  NCT of Delhi → Delhi, J&K → Jammu and Kashmir).
- PIN: remove one internal space (`560 102` → `560102`).

## Normalisation that is NOT safe
- Changing city names automatically. Both the old and new forms remain in use (Bangalore/Bengaluru,
  Gurgaon/Gurugram, Bombay/Mumbai) and couriers accept both. Suggest, don't overwrite.
- Title-casing everything (breaks "HSR", "MG Road", "C/o").
- Removing "Near ...", "Opp. ...", "Behind ..." (landmarks are part of the address in India).
- Forcing the city to match the PIN directory's office name (office names are post-office names,
  not necessarily the city people use).

## Common pitfalls
- A **district** is not a city; many PINs in a district belong to different towns.
- Metro areas span several districts and sometimes several states (Delhi NCR: Delhi, Haryana,
  Uttar Pradesh), so state matters for GST place of supply.
- Rural addresses often lack street names; village + post office + tehsil/taluka + district is normal.
- Military addresses use APS/FPO PINs (9xxxxx) and unit formats. Don't reject them.
- Address-proof documents (Aadhaar, utility bills) use different layouts. Don't require exact
  match with KYC documents for delivery addresses.
- For GST invoices, the **state** of the delivery address can change the tax (IGST vs CGST+SGST).
  See the `gst-invoicing` skill.
