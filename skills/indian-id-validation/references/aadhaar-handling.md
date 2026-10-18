# Aadhaar handling rules for developers

> Not legal advice. This summarises UIDAI material as of the last-verified date in
> [sources.md](sources.md). Whether your organisation may collect or store Aadhaar
> numbers at all depends on the law and UIDAI's permissions for your use case.
> Confirm with counsel and current UIDAI circulars.

## What the law and regulations say (quoted or closely paraphrased)

- **Aadhaar Act 2016, s.29(1):** core biometric information shall not be shared with
  anyone for any reason, or used for any purpose other than Aadhaar generation and authentication.
- **Aadhaar (Sharing of Information) Regulations 2016, reg. 6:**
  - (1) The Aadhaar number of an individual shall not be published, displayed or posted
    publicly by any person, entity or agency.
  - (2) Anyone holding Aadhaar numbers shall ensure the security and confidentiality of
    the numbers and of any record or database containing them.
  - (3) No entity shall make public any database or record containing Aadhaar numbers
    unless the numbers have been redacted or blacked out, in print and electronic form.
  - (4) No entity shall require an individual to transmit their Aadhaar number over the
    Internet unless the transmission is secure and the number is encrypted.
- **UIDAI compliance checklist for Sub-AUA/Sub-KUA (v2.0, May 2025):**
  - Entities *allowed* to store Aadhaar numbers must store them and connected data
    (e.g. eKYC XML) only in a separate secure **Aadhaar Data Vault (ADV)**, referenced by
    a **reference key**, in a single logical ADV instance.
  - Only trusted communication in/out of the vault, ideally via dedicated APIs, with
    strong access control, monitoring, logging and alerts.
  - Display of the full number only to the Aadhaar holder or roles with functional
    necessity; **by default all other display is masked so only the last four digits show**.
- **UIDAI, "What is Masked Aadhaar?":** masking replaces the first 8 digits with
  characters like `xxxx-xxxx`, leaving the last 4 digits visible.

## Developer checklist

Collection
- [ ] Is collecting Aadhaar actually required? Prefer other KYC documents if allowed.
- [ ] Explain why it is collected (purpose) at the point of collection.
- [ ] Transmit only over TLS; encrypt the number in the request payload if the
      platform allows. Never in query strings or URL paths.

Validation
- [ ] Client and server: strip spaces/hyphens, require 12 digits, Verhoeff checksum.
- [ ] Error messages never echo the number back.
- [ ] Sandbox/test mode can bypass the checksum (UIDAI test UID `999999990019` fails it).

Storage
- [ ] Default: **don't store it.** Keep the masked form (`XXXX XXXX 1234`) or a token.
- [ ] If storage is permitted: separate encrypted vault (ADV), reference keys in the
      main database, keys in an HSM/KMS, access only via a dedicated service, audited.
- [ ] Never in plain columns, search indexes, caches, data warehouses, backups outside
      the vault, CSV exports, or spreadsheets.
- [ ] Never store or forward biometric data.

Logging, errors and analytics
- [ ] Mask before the value reaches loggers, APM/error trackers (Sentry etc.), analytics,
      LLM prompts, or support tooling. Add a log scrubber for 12-digit sequences as
      defence in depth.
- [ ] Redact request bodies for Aadhaar fields in HTTP access logs and API gateways.

Display and documents
- [ ] UI shows `XXXX XXXX 1234` by default; full number only to the holder (and only
      when they ask), never to support agents by default.
- [ ] Uploaded Aadhaar card images: ask users to upload the **masked e-Aadhaar**, or
      redact the first 8 digits before storing; don't keep unredacted copies.

Testing
- [ ] Use synthetic numbers generated with a Verhoeff check digit. Never real ones.

## Masking reference implementation

```python
def mask_aadhaar(value: str) -> str:
    digits = "".join(c for c in value if c.isdigit())
    return f"XXXX XXXX {digits[-4:]}" if len(digits) == 12 else "XXXX XXXX XXXX"
```

```js
export const maskAadhaar = (v) => {
  const d = String(v).replace(/\D/g, "");
  return d.length === 12 ? `XXXX XXXX ${d.slice(-4)}` : "XXXX XXXX XXXX";
};
```

Never mask by showing the *first* digits, and never reveal more than the last four.
