# Open verification items

Everything here is marked `TODO(verify)` in the skills. Regenerate the raw list with
`python3 tools/check_skills.py --todos`. If you can confirm one from an official source, fix it, cite
the source in that skill's `references/sources.md`, and remove the item here.

Last reviewed: 2026-10-18.

## indian-id-validation
- [ ] **GSTIN check-character algorithm:** no official GSTN/CBIC publication found. The mod-36
      algorithm matches all 19 real published GSTINs tested.
- [ ] **GST state code 99 label:** sources disagree ("Centre Jurisdiction" vs "Other Country").

## gst-tax-calculation
- [ ] Goods covered by Schedules IV-VI (3%, 0.25%, 1.5%) of Notification 9/2025-CT(Rate).
- [ ] Full current consolidated reverse-charge list (Notification 13/2017-CT(Rate) as amended).

## gst-invoicing
- [ ] Whether rule 46(e)'s ₹50,000 unregistered-recipient threshold has changed since the 2020
      consolidation.
- [ ] Whether Ladakh (code 38) is covered by UTGST as "other territory".

## tds-basics
- [ ] How the no-PAN 20% rule (s.397(2)) applies to salary TDS under s.392.
- [ ] Section 393 table serial numbers other than 6(i), 6(iii), 8(ii), 8(v); scope of s.393(2)/(3).
- [ ] Threshold treatment of director's sitting fees / commission.
- [ ] New-Act TDS return and certificate form numbers (other than Form 141 and Form 168).

## upi-payments
- [ ] Current NPCI UPI Linking Specification (we used v1.6 draft, 2017, via a mirror; npci.org.in
      blocks automated access).
- [ ] NPCI rules on unsigned merchant intents.
- [ ] Exact NPCI API-usage limits (status check, balance enquiry) from the circular itself (news reports only).
- [ ] P2P collect discontinuation circular (29 Jul 2025) text (news reports only).
- [ ] Any official character-level grammar for VPAs.

## indian-addresses
- [ ] Postal circle ranges covering DNH&DD, Goa, Puducherry, Lakshadweep, Sikkim, Andaman & Nicobar,
      and the other north-eastern states within "79 North Eastern".

## dpdp-privacy
- [ ] Commencement notification(s) for individual sections of the DPDP Act (the Rules' phasing is verified).
- [ ] Sector-specific breach timelines (CERT-In, RBI, SEBI, IRDAI) that apply alongside DPDP.

## indian-dates-and-fiscal-year
- [ ] Whether the Legal Metrology (Indian Standard Time) Rules have been finalised (draft seen, 2025).

## Sites that blocked verification from our build environment
`npci.org.in` (HTTP 403), `incometaxindia.gov.in` (403), `einvoice1.gst.gov.in` (connection reset),
`data.gov.in` downloads (503), several `*.nic.in` hosts (TLS certificate chain). Facts from these were
taken from search-engine extracts of the official URLs and are labelled `[extract]` in `sources.md`.
A contributor with direct access can upgrade them to `[page]`.
