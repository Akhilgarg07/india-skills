# DPDP build checklist (engineering)

> Not legal advice. Section/rule references are to the DPDP Act, 2023 and DPDP Rules, 2025.

## Data inventory (do first)
- [ ] List every personal data field, its source, purpose(s), lawful ground (consent / which
      legitimate use), storage location(s), processors, retention period and legal retention basis.
- [ ] Flag children's data, financial data, health data, identifiers (Aadhaar, PAN), location.
- [ ] Map cross-border flows (cloud regions, SaaS vendors).

## Consent and notice
- [ ] Notice is standalone, plain language, itemised data + specific purposes (rule 3).
- [ ] Language selector: English plus Eighth Schedule languages on request (s.5(3), s.6(3)).
- [ ] Separate, unticked toggles per optional purpose (marketing, personalisation, analytics).
- [ ] Core service doesn't depend on consent to unrelated processing.
- [ ] Consent receipt stored and visible to the user.
- [ ] Withdrawal from the same surface, same effort. Propagated to processors (webhooks / APIs / jobs).
- [ ] Re-notice existing users (s.5(2)).
- [ ] Consent Manager integration planned if you expect to accept consent via one (rule 4, from ~Nov 2026).

### Consent record data model (suggested)
```sql
create table consent_event (
  id              uuid primary key,
  principal_id    text not null,          -- your user id, not raw PII
  purpose         text not null,          -- e.g. 'orders', 'marketing_email'
  action          text not null check (action in ('given','withdrawn')),
  notice_version  text not null,          -- hash / version of the notice shown
  language        text not null,
  channel         text not null,          -- 'web', 'android', 'ios', 'call-centre', 'consent-manager'
  evidence        jsonb,                  -- UI element id, IP/device (minimised), CM artefact id
  occurred_at     timestamptz not null default now()
);
```
Derive current state per (principal, purpose) from the latest event. Never update in place.

## Rights requests (90-day maximum)
- [ ] Published request method and required identifier (rule 14(1)).
- [ ] Identity verification proportional to risk; support nominees (s.14, rule 14(4)).
- [ ] Access export: data summary, processing activities, list of other fiduciaries/processors shared with (s.11).
- [ ] Correction / completion / update flows (s.12(2)).
- [ ] Erasure job that respects legal holds (KYC, tax, accounting), with processor erasure (s.12(3), s.8(7)).
- [ ] Ticketing with SLA timers and audit trail. Grievance responses include DPO/contact details (rule 9).

## Retention and erasure
- [ ] Retention schedule per field/purpose; automated deletion jobs; backups age out.
- [ ] Logs + associated personal data kept ≥ 1 year for security purposes, then erased (rules 6, 8(3)).
- [ ] Large e-commerce/gaming/social platforms: 3-year inactivity erasure with 48-hour advance
      notice (Third Schedule, rule 8).

## Security (rule 6 minimums)
- [ ] Encryption at rest/in transit; masking/tokenisation for identifiers.
- [ ] Least-privilege access, MFA for admin, access reviews.
- [ ] Centralised logs of access to personal data; alerting; 1-year retention.
- [ ] Backups and DR tested.
- [ ] Processor contracts include security obligations and breach notice to you.

## Breach runbook
1. **Detect and triage.** Is personal data affected? (Any unauthorised processing, accidental
   disclosure, acquisition, sharing, use, alteration, destruction or loss of access counts.)
2. **Hour 0:** open an incident, preserve logs, contain.
3. **Without delay:** initial intimation to the **Board** (nature, extent, timing, location,
   likely impact) and notification to **each affected person** via their account/registered contact
   (what happened, consequences, mitigation, what they should do, contact person).
4. **Within 72 hours** of becoming aware: detailed report to the Board (updated description;
   facts, circumstances and reasons; mitigation; findings on who caused it; remedial measures;
   report on notifications sent). Ask in writing if you need longer.
5. Post-incident review; fix root cause; update DPIA (if SDF).
6. Keep sector timelines in mind too (e.g. CERT-In and sector regulators have their own reporting
   rules; `TODO(verify)` their current timelines).

## Children
- [ ] Age gate at sign-up; treat unknown age conservatively where the service is likely used by children.
- [ ] Verifiable parental consent flow (rule 10): existing reliable identity/age data, or a token
      from an authorised entity / DigiLocker.
- [ ] Disable tracking, behavioural monitoring and targeted ads for under-18 accounts (s.9(3)).
- [ ] Check Fourth Schedule exemptions before relying on one.

## Vendor / processor management
- [ ] Contract with every processor (s.8(2)); right to audit; deletion on termination; breach notice duty.
- [ ] Keep a list of processors for access requests (s.11(1)(b)).
