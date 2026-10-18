# UPI linking parameters: full table

Source: NPCI, *UPI Linking Specifications, Version 1.6 (Draft), November 2017*, "Common URL
specifications for deep linking and proximity integration" (see [sources.md](sources.md) for
how it was accessed). NPCI may have issued later versions; `TODO(verify)` against the current
NPCI specification before relying on optional/secure fields.

URI form: `upi://pay?param-name=param-value&param-name=param-value&...`
All PSP apps "must mandatorily implement listening to 'UPI' links ... for QR, intent, NFC, BLE,
UHF etc." M = mandatory, C = conditional, O = optional.

| Param | Type | Static | Dynamic | Maps to UPI API | Notes from the spec |
|---|---|---|---|---|---|
| `pa` | String | M | M | Payee → addr | Payee VPA |
| `pn` | String | M | M | Payee → name | Payee name |
| `mc` | String | O | O | Payee → mcc | Merchant code; if present pass as it is |
| `tid` | String | O | O | Txn → id | Must be PSP-generated when present; merchants may get it from their PSP |
| `tr` | String | O | C | Txn → refId | Order no., subscription no., bill id, booking id...; **mandatory for merchant transactions and dynamic URL generation** |
| `tn` | String | O | O | Txn → note | Short description |
| `am` | String | O | M | Payee → Amount → value | Decimal format; if absent the amount is editable |
| `mam` | String | O | C | Txn → Rules → MINAMOUNT | Minimum amount if different from `am` |
| `cu` | String | O | O | Payee → Amount → curr | Only `INR` supported |
| `url` | String | O | O | TxnrefUrl | Transaction details / digital goods; must relate to the transaction, never unsolicited content; http or https |
| `mode` | 2 digits | M* | M* | Txn initiationMode | `00` default, `01` QR, `02` secure QR, `04` intent, `05` secure intent, `06` NFC, `07` BLE, `08` UHF, `15` SEBI |
| `sign` | String | M* | M* | – | Base64 digital signature; must be the last tag |
| `orgid` | 6 digits | M* | M* | – | PSP org id; `000000` for merchant-initiated intent/QR |
| `mid` | ≤ 20 | O | O | Payee merchant mid | Merchant id |
| `msid` | ≤ 20 | O | O | Payee merchant sid | Store id |
| `mtid` | ≤ 20 | O | O | Payee merchant tid | Terminal id |
| `Query` | JSON ≤ 99 | O | O | future use | – |

\* In v1.6 these are listed as mandatory for the **signed** intent/QR scheme. Ordinary
P2P-style links that payer apps accept in practice contain only `pa`, `pn` and optionally
`am`, `cu`, `tn`, `tr`.

Other rules in the spec:
- When reading a QR/intent/NFC/BLE, "all parameters must be read and passed to online message".
- "If any tag is not present it can be dropped or passed as null."
- Signing (merchant-initiated): the merchant or acquiring bank generates a key pair; the public
  key is uploaded to UPI by the acquiring bank; the merchant signs the entire URI except
  `&sign=` (SHA256 with RSA) and appends the Base64 signature as the last parameter; payer PSPs
  download and cache merchant keys daily and verify.

Usage patterns in the spec: in-app payment via intent on the same phone; dynamic QR on a PoS or
printed bill; static QR with only payee address and name, where "customer, after scanning,
should enter the amount"; QR on a TV screen (DTH).
