---
name: dpdp-privacy
description: Practical engineering checklist for India's Digital Personal Data Protection Act 2023 and DPDP Rules 2025 - applicability, phased commencement (Rules notified Nov 2025; most obligations from about May 2027), consent and notice design, withdrawal, legitimate uses, purpose and storage limitation (erasure, 1-year log retention), security safeguards, breach intimation (Data Principals without delay; Board within 72 hours), Data Principal rights (90-day response), children's data (verifiable parental consent; no tracking or targeted ads), Consent Managers and Significant Data Fiduciaries. Use when designing sign-up/consent flows, privacy notices, data retention or deletion jobs, breach response runbooks, DSAR/rights endpoints, or reviewing an Indian product for DPDP readiness. Not legal advice.
license: MIT
metadata:
  version: "0.1.0"
  last-verified: "2026-10-18"
---

# DPDP privacy checklist (India)

> **Not legal advice.** This is an engineering checklist summarising the DPDP Act, 2023 and
> DPDP Rules, 2025 as of the last-verified date. Rules, notifications, Board guidance and
> sector rules (RBI, SEBI, IRDAI, health) change and can impose more. Get legal review.

## Key terms
- **Data Principal:** the individual (for a child, includes the parent/lawful guardian).
- **Data Fiduciary:** decides why and how personal data is processed (you, usually).
- **Data Processor:** processes on a fiduciary's behalf (your cloud, CRM, email vendor).
- **Consent Manager:** a Board-registered, India-incorporated platform to give, manage, review and
  withdraw consent.
- **Significant Data Fiduciary (SDF):** notified by the Government; extra duties.
- **Child:** under **18** years.

## Does it apply?
- Applies to **digital personal data** processed in India (collected digitally, or collected on paper
  and digitised later), and to processing **outside India** connected with offering goods/services to
  people in India.
- Doesn't apply to purely personal/domestic use, or to data the person themselves made publicly
  available (or that law requires to be published).

## When obligations bite (phased)
- Act enacted 11 Aug 2023. **Rules published 13 Nov 2025** (PIB: notified 14 Nov 2025).
- Immediately: definitions, Data Protection Board (rules 1, 2, 17-21). The Board is digital, appeals
  go to TDSAT.
- **+1 year (≈ Nov 2026):** Consent Manager registration (rule 4).
- **+18 months (≈ May 2027):** notice, security, breach intimation, retention/erasure, contact
  details, children, SDF duties, rights, cross-border (rules 3, 5-16, 22, 23).
- `TODO(verify)` the commencement dates of individual Act sections (notified separately).
- **Build now.** Consent records, retention jobs and breach runbooks take longer than the runway.

## 1. Lawful ground: consent or a legitimate use
- Process only for a **lawful purpose** with **consent** or a listed **legitimate use** (s.4, s.7):
  data the person **voluntarily provided for a specified purpose** without objecting (e.g. sending a
  receipt they asked for), State subsidies/services, legal obligations, court orders, **medical
  emergencies**, disasters and public order, and **employment** purposes.
- Don't bundle: consent must be **free, specific, informed, unconditional, unambiguous, with a clear
  affirmative action**, and limited to data **necessary** for the purpose (s.6(1)). Pre-ticked boxes,
  "by continuing you agree", and consent for unneeded data (e.g. contacts for a telemedicine app)
  don't qualify.
- Any consent term that waives legal rights (e.g. the right to complain to the Board) is **invalid** (s.6(2)).

## 2. Notice (s.5, rule 3)
Show it with or before the consent request, standalone and in plain language:
- an **itemised list of the personal data** and the **specific purpose(s)** and the goods/services or
  uses it enables;
- a **link** to your website/app and how to **withdraw consent** (as easy as giving it), **exercise
  rights**, and **complain to the Board**;
- available in **English or any Eighth Schedule language** on request (s.5(3), s.6(3));
- contact of the DPO or another responsible person.
- Existing users who consented before commencement must also get a notice "as soon as reasonably
  practicable" (s.5(2)).

## 3. Consent records and withdrawal
- Store **who, what notice version, which purposes, when, how (UI/channel), and withdrawals**. The
  fiduciary must **prove** notice and consent if challenged (s.6(10)).
- Withdrawal must be as easy as consent (one tap if consent was one tap). On withdrawal, stop
  processing within a reasonable time **and make your processors stop** (s.6(6)), unless law requires otherwise.
- Make consent **per purpose** (orders vs marketing vs analytics), not one global flag.

## 4. Purpose and storage limitation
- **Erase** when consent is withdrawn or the purpose is no longer served, whichever is earlier, and
  make processors erase too (s.8(7)), unless law requires retention (e.g. KYC, tax records).
- Large e-commerce (≥ 2 crore registered users), online gaming (≥ 50 lakh) and social media (≥ 2 crore)
  fiduciaries: data of users inactive for **3 years** is deemed no longer needed (Third Schedule).
  Warn the user **48 hours** before erasure (rule 8(2)).
- **Keep processing logs and associated personal data for at least 1 year** (rule 6(1)(e), rule 8(3))
  for security investigation, even after account deletion. Then erase unless another law says otherwise.
- Keep data **accurate and complete** when it's used for decisions about the person or shared (s.8(3)).

## 5. Security safeguards (s.8(5), rule 6)
Minimum: encryption/obfuscation/masking/tokenisation; access control; logging, monitoring and review
of access; backups and continuity; **1-year log retention**; security clauses in processor contracts;
technical and organisational measures. Failing to take reasonable safeguards carries the **highest
penalty (up to ₹250 crore)**.

## 6. Personal data breach (s.8(6), rule 7)
- **Affected Data Principals: without delay**, via their account or registered contact, in plain
  language: what happened (nature, extent, timing), likely consequences, mitigation done, steps they
  can take, and a contact person.
- **Board:** an initial description **without delay**; a detailed report **within 72 hours** of
  becoming aware (or a longer period the Board allows on written request), covering facts and causes,
  mitigation, findings about who caused it, remedial measures, and a report on the notifications sent.
- There is **no materiality threshold** in the text: every personal data breach is reportable.
  Penalty for failing to notify: up to **₹200 crore**.
- Runbook: [references/checklist.md](references/checklist.md#breach-runbook).

## 7. Data Principal rights (s.11-14, rule 14)
- **Access** (summary of data and processing, and who it was shared with), **correction, completion,
  updating, erasure**, **grievance redressal**, **nomination** (someone to act on death/incapacity).
- Publish how to make requests and what identifier is needed. **Respond within 90 days** at most.
- People must use your grievance channel before going to the Board, so make it real and tracked.

## 8. Children and persons with disabilities (s.9, rules 10-12)
- Get **verifiable consent of a parent/lawful guardian** before processing a child's data. Check the
  parent is an identifiable **adult** using reliable identity/age details you already hold, or a
  **virtual token** from an authorised entity (e.g. via DigiLocker).
- **No tracking, behavioural monitoring or targeted advertising directed at children**, and no
  processing likely to harm a child's well-being. Penalty: up to **₹200 crore**.
- Limited exemptions (Fourth Schedule) exist for specified fiduciaries and purposes, such as
  healthcare, education and child safety. Check them before relying on one.

## 9. Processors, transfers, contact
- Use processors only under a **valid contract**; you stay responsible for them.
- Cross-border transfers are allowed except where the Government restricts them (s.16, rule 15).
  SDFs may face localisation for notified data categories.
- Publish the **DPO / contact person** on your site/app and in every rights response (rule 9).
- SDFs: DPO based in India, annual **DPIA and audit**, algorithmic due diligence (s.10, rule 13).

Detailed build checklist, data model and runbooks: [references/checklist.md](references/checklist.md).
Sources (Act and Rules text, PIB): [references/sources.md](references/sources.md).
