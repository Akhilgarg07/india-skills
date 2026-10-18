# Reverse charge mechanism (RCM): reference

> Not tax advice. The notified list (Notification 13/2017-Central Tax (Rate) for services and
> its IGST counterpart; a separate notification covers goods) is amended frequently.

## Legal basis

- **Section 9(3) CGST Act / 5(3) IGST Act:** the Government may notify categories of supply
  of goods or services on which tax "shall be paid on reverse charge basis by the
  recipient", and the Act applies to the recipient as if it were the person liable.
- **Section 9(4) CGST Act (as substituted from 1 Feb 2019):** the Government may notify "a
  class of registered persons" who must pay tax under reverse charge on "specified categories
  of goods or services" received from an **unregistered** supplier. Before 2019, 9(4) applied
  to all purchases from unregistered suppliers. It no longer does.
- **Section 9(5):** for notified services supplied through an e-commerce operator, the
  operator pays the tax. This is not RCM, but it is often confused with it.

## Services under RCM (from the GST Council's notified list; examples)

| Service | Supplier | Recipient who pays |
|---|---|---|
| Any service from a person in a non-taxable territory (import of services) | Person outside India | Person in India (other than non-taxable online recipient) |
| Goods transport by road by a GTA | Goods Transport Agency | Factory, society, co-operative, registered person, body corporate, partnership firm/AOP, casual taxable person |
| Legal services | Individual advocate / firm of advocates | Business entity |
| Arbitral tribunal services | Arbitral tribunal | Business entity |
| Sponsorship | Any person | Body corporate or partnership firm |
| Services by Government / local authority (with exclusions: renting of immovable property, some postal, aircraft/vessel and transport services) | Government / local authority | Business entity |
| Director's services | Director of a company / body corporate | That company / body corporate |
| Insurance agent services | Insurance agent | Insurer |
| Recovery agent services | Recovery agent | Bank / financial institution / NBFC |
| Ocean freight for imports | Person in non-taxable territory | Importer |

Later amendments added and removed entries. For example, renting of commercial property by an
unregistered person to a registered person was under RCM from 10 Oct 2024 (notification
09/2024-CT(Rate)) and moved to forward charge by 07/2025-CT(Rate) dated 16 Jan 2025.
`TODO(verify):` take the full current list from the latest consolidated 13/2017-CT(Rate)
before relying on any entry.

## Compliance points for software

- **Invoice:** every tax invoice must state whether tax is payable on reverse charge
  (rule 46 CGST Rules). Same for receipt and refund vouchers.
- **Collection:** the supplier does not charge GST to the customer on an RCM supply. The
  invoice total payable to the supplier excludes tax.
- **Payment:** the recipient must pay RCM tax through the **electronic cash ledger**; input
  tax credit can't be used to discharge it. After paying, the recipient may take ITC if eligible.
- **Registration:** a person liable to pay tax under RCM must register; the turnover
  threshold does not apply.
- **Time of supply under RCM** (as described in CBIC's RCM flyer):
  - Goods: earliest of receipt of goods; payment date (books or bank debit, whichever is
    earlier); or the day after 30 days from the invoice date.
  - Services: earliest of payment date; or the day after 60 days from the invoice date.
- **Advances** paid for RCM supplies are also liable to GST under RCM.
- **Returns:** RCM inward supplies are reported separately; outward invoices attracting RCM
  are reported invoice-wise in GSTR-1.
