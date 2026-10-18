# Place of supply: reference (IGST Act 2017)

> Not tax advice. Summarised from the IGST Act (GST Council copy) and CBIC/GST Council
> material in [sources.md](sources.md). Edge cases need a professional.

## Why it matters
- **Inter-state** (IGST) when the supplier's location and the place of supply are in two
  different States, two different UTs, or a State and a UT (s.7(1), 7(3)).
- **Intra-state** (CGST + SGST/UTGST) when both are in the same State/UT (s.8).
- Always inter-state: imports, exports, and supplies **to or by an SEZ unit/developer**
  (s.7(2), 7(4), 7(5)).
- Separate registrations of one PAN in different states are **distinct persons**. Supplies
  between them are taxable (s.8 Explanation 1, s.25).

## Goods (s.10), other than imports/exports

| Situation | Place of supply |
|---|---|
| Supply involves movement of goods | location where movement **terminates** for delivery to the recipient (10(1)(a)) |
| Delivered to a third party on the direction of a buyer ("bill to / ship to") | **principal place of business of the buyer** who directed it (10(1)(b)) |
| Goods to an **unregistered** person (from 1 Oct 2023) | address of the person **recorded in the invoice** (state name is enough); if none, the supplier's location (10(1)(ca)) |
| No movement | location of goods at delivery (10(1)(c)) |
| Assembled/installed at site | site of installation (10(1)(d)) |
| On board a conveyance (train, aircraft, vessel, vehicle) | where taken on board (10(1)(e)) |
| Imports / exports (s.11) | location of the importer / location outside India |

E-commerce B2C: record the **delivery address** as the recipient's address so the place of
supply is the delivery state (53rd GST Council agenda).

## Services where supplier and recipient are both in India (s.12)

General rule (12(2)):
- to a **registered** person → location of that person;
- to an **unregistered** person → location of the recipient where an address is on record,
  otherwise the location of the supplier.

Special rules (examples):

| Service | Place of supply |
|---|---|
| Related to immovable property (architects, interior decorators, construction, renting), hotel/guest house lodging, function venues | where the property is located (12(3)) |
| Restaurant, catering, personal grooming, fitness, beauty, health services | where actually performed (12(4)) |
| Training and performance appraisal | registered: recipient's location; else where performed (12(5)) |
| Admission to events, amusement parks | where the event is held or the park is located (12(6)) |
| Organising events, sponsorship of events | registered: recipient's location; else where the event is held (12(7)) |
| Transport of goods, incl. courier | registered: recipient's location; else where goods are handed over (12(8)) |
| Passenger transport | registered: recipient's location; else where the passenger embarks (12(9)) |
| Telecom, banking, insurance, advertising to Government, etc. | see 12(10)-(14) |

Cross-border services (supplier or recipient outside India) follow **section 13** (often the
location of the recipient, with many exceptions). Exports of services must meet s.2(6)
conditions (payment in convertible foreign exchange or INR where RBI permits, etc.).

## Practical rules for software

- Ask for and store the recipient's **state code** and whether they are registered.
- Goods: default the place of supply to the **ship-to state**; let the user override for
  bill-to/ship-to cases.
- Services B2B: default to the **recipient GSTIN's state**.
- Services B2C: the recipient's address state if captured, else the supplier's state.
- Show "Place of Supply: Maharashtra (27)" on the invoice.
- Exports in e-invoice JSON: recipient GSTIN `URP`, state code `96`, PIN `999999`, POS `96`.
