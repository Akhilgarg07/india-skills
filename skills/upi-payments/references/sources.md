# Sources: upi-payments

**Last verified: 2026-10-18**

Method key: **[page]** = official page/PDF downloaded and read; **[mirror]** = an official
document read from a third-party copy because the official host refused our requests
(npci.org.in returns HTTP 403 to automated clients); **[extract]** = search-engine extract of an
official URL; **[reported]** = news reports of an official circular. Treat [reported] items as
lower confidence.

## Link / QR format
- [mirror] NPCI, *UPI Linking Specifications Version 1.6 (Draft)*, November 2017 (parameter
  table, mode codes, signing, QR usage). Copy read at https://www.labnol.org/files/linking.pdf ;
  official publisher: National Payments Corporation of India, https://www.npci.org.in/
  `TODO(verify):` locate the current version on npci.org.in.

## Limits
- [extract] RBI, Statement on Developmental and Regulatory Policies, 20 Dec 2023: UPI limit for
  hospitals and educational institutions proposed from ₹1 lakh to ₹5 lakh per transaction; RBI
  Payment Systems Report (Jan 2025) confirms the enhancement.
  https://rbidocs.rbi.org.in/rdocs/Publications/PDFs/PSR270120251BEE95CF47F2426B9740075D405FA070.PDF
- [extract] RBI Bulletin, April 2025 (Statement on Developmental and Regulatory Policies): P2P
  remains capped at ₹1 lakh; P2M generally ₹1 lakh with some use cases at ₹2 lakh / ₹5 lakh; NPCI
  enabled to decide P2M limits with banks and stakeholders.
  https://rbidocs.rbi.org.in/rdocs/Bulletin/PDFs/0BULL22042025F03F83AE118C4B3B84E662D980C8DE33.PDF

## NPCI operational circulars (2025)
- [reported] NPCI circular dated 29 Jul 2025: no P2P collect transaction to be initiated, routed
  or processed after 1 Oct 2025. E.g. https://www.businesstoday.in/personal-finance/banking/story/npci-to-tighten-upi-rules-peer-to-peer-collect-feature-to-end-in-october-489244-2025-08-13
- [reported] NPCI notification of 21 May 2025 on API usage from 1 Aug 2025 (check-status at most
  3 times with 90-second gaps; balance enquiry 50/day per app). E.g.
  https://www.scconline.com/blog/?p=354994
  `TODO(verify):` read both circulars on npci.org.in.

## General
- Payment-status practices (server-side verification, idempotency, reconciliation) are
  engineering best practice consistent with the spec's statement that a link is a payment
  *request*. They are not a regulatory text.

## Open items to verify
- Current NPCI UPI linking specification version and any rules on unsigned merchant intents.
- Exact NPCI API-usage limits (status check, balance enquiry) and P2P collect circular text.
- Any official character-level grammar for VPAs.
