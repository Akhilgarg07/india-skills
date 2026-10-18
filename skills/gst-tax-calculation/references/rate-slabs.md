# GST rate slabs: detail and history

> Not tax advice. Check the current rate notification for the specific HSN/SAC entry.

## Legal ceiling

Section 9(1) CGST Act: CGST is levied "at such rates, not exceeding twenty per cent, as
may be notified". SGST/UTGST mirrors it, so the highest combined intra-state rate is 40%
(20% + 20%), which equals the IGST ceiling.

## Goods rate notification from 22 September 2025

Notification No. 9/2025-Central Tax (Rate), dated 17 Sep 2025, superseded notification
1/2017-CT(Rate). Its companion for inter-state supplies is 9/2025-Integrated Tax (Rate).

| Schedule | CGST | IGST (= total GST) | Notes |
|---|---|---|---|
| I | 2.5% | 5% | merit rate |
| II | 9% | 18% | standard rate; from 1 Feb 2026 also covers bidi |
| III | 20% | 40% | special rate; from 1 Feb 2026 also pan masala, cigarettes and other tobacco (not bidi), nicotine inhalation products |
| IV | 1.5% | 3% | `TODO(verify):` goods covered (traditionally precious metals and jewellery) |
| V | 0.125% | 0.25% | `TODO(verify):` goods covered (traditionally rough precious/semi-precious stones) |
| VI | 0.75% | 1.5% | `TODO(verify):` goods covered |
| VII | 14% | 28% | tobacco goods kept on old rates; **omitted from 1 Feb 2026** |

Amendment: Notification 19/2025-CT(Rate) dated 31 Dec 2025 (effective 1 Feb 2026) moved the
tobacco and pan masala items into Schedules II and III and omitted Schedule VII.
Notification 03/2025-Compensation Cess (Rate) set compensation cess on those goods to Nil
from 1 Feb 2026, and a retail-sale-price (RSP) based valuation was introduced for them.

Services rates are in separate notifications (the 11/2017-CT(Rate) series, as amended). The
same 5% / 18% / 40% structure applies. Some services have a 5%-without-ITC option alongside
18%-with-ITC (e.g. passenger transport by road; hotel accommodation up to ₹7,500 per unit per
day is 5% without ITC).

## Before 22 September 2025 (for historical invoices)

The main slabs were 5%, 12%, 18% and 28%, with compensation cess on top for many 28% goods
(e.g. cars, aerated drinks, tobacco). Reprinting, amending or crediting an old invoice uses
the rate applicable on its time of supply (section 14 CGST Act covers supplies straddling
a rate change).

## Examples announced by the GST Council (56th meeting)

These are illustrations only. Always look up the HSN/SAC entry.
- 12% to 5%: bicycles and parts, renewable-energy devices, many processed foods.
- 28% to 18%: small cars (petrol/LPG/CNG up to 1200 cc and 4000 mm; diesel up to 1500 cc
  and 4000 mm), motorcycles up to 350 cc, three-wheelers, buses, trucks, ACs, dishwashers,
  all TVs and monitors.
- 40%: mid-size and large cars (above 1500 cc or 4000 mm), motorcycles above 350 cc,
  aerated and other non-alcoholic beverages, yachts, private aircraft, pan masala and tobacco.
- Nil: individual life and health insurance policies; UHT milk; chapati/roti, paratha;
  33 lifesaving drugs.
- Coal: 5% + ₹400/tonne compensation cess became 18% with no cess.

## Rate-table design

```
gst_rate(hsn_or_sac, effective_from, effective_to, igst_rate, condition_note)
```
- Look up by item code **and** date of supply.
- Store the IGST/total rate. Derive CGST = SGST = rate / 2.
- Keep the source notification number on each row for audit.
