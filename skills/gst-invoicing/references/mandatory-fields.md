# Tax invoice: full particulars and related rules

> Not tax advice. Text summarised from CGST Rules 46-48 (CBIC consolidated text) and
> later amendments noted in [sources.md](sources.md).

## Rule 46: particulars of a tax invoice

(a) name, address and GSTIN of the supplier;
(b) a consecutive serial number **not exceeding sixteen characters**, in one or multiple
    series, containing alphabets or numerals or the special characters hyphen/dash `-` and
    slash `/`, and any combination thereof, **unique for a financial year**;
(c) date of its issue;
(d) name, address and GSTIN or UIN, if registered, of the recipient;
(e) name and address of the recipient and the address of delivery, with the **name of the
    State and its code**, if the recipient is unregistered and the value of the taxable
    supply is **₹50,000 or more**;
(f) the same details if the recipient is unregistered, the value is below ₹50,000, and the
    recipient **requests** that they be recorded;
(g) HSN code for goods or services (number of digits notified; see below);
(h) description of goods or services;
(i) quantity in case of goods, and unit or Unique Quantity Code;
(j) total value of supply;
(k) taxable value, taking into account discount or abatement;
(l) rate of tax (central, State, integrated, UT tax or cess);
(m) amount of tax charged (central, State, integrated, UT tax or cess);
(n) place of supply with the name of the State, for inter-State supplies;
(o) address of delivery where different from the place of supply;
(p) whether the tax is payable on reverse charge basis;
(q) signature or digital signature of the supplier or authorised representative
    (not required for an electronic invoice issued under the IT Act, 2000);
(r) QR code with embedded Invoice Reference Number, where the invoice is issued under
    rule 48(4) (e-invoicing).

`TODO(verify):` the ₹50,000 figure in clauses (e)/(f) is from the 2020 consolidated rules;
confirm no later amendment changed it.

### Provisos worth encoding
- **Exports / SEZ:** endorse "SUPPLY MEANT FOR EXPORT/SUPPLY TO SEZ UNIT OR SEZ DEVELOPER
  FOR AUTHORISED OPERATIONS ON PAYMENT OF INTEGRATED TAX" or "... UNDER BOND OR LETTER OF
  UNDERTAKING WITHOUT PAYMENT OF INTEGRATED TAX", and instead of clause (e) show the
  recipient's name and address, the delivery address and the **country of destination**.
- **Consolidated B2C invoice:** a supplier (other than multiplex cinema admission) need not
  issue an invoice per sale to an unregistered recipient who doesn't ask for one, but must
  issue a consolidated tax invoice for such supplies at the close of each day.
- **Dynamic QR on B2C invoices:** registered persons with aggregate turnover above **₹500
  crore** must print a Dynamic QR code on B2C invoices (Notification 14/2020-CT, in force from
  1 Dec 2020). Invoices to UIN holders count as B2C for this.
- The earlier proviso for monthly consolidated invoices on s.9(4) purchases was omitted
  from 1 Nov 2024.

## HSN / SAC digits (Notification 78/2020-Central Tax, from 1 Apr 2021)

| Aggregate turnover in the preceding FY | Digits on tax invoice |
|---|---|
| Up to ₹5 crore | 4 (may be omitted on B2C invoices) |
| More than ₹5 crore | 6 (6 or 8 accepted) |

Services use SAC codes from the "Scheme of Classification of Services" (chapter 99), e.g.
`998313` IT consulting and support, `998314` IT design and development, `998315` hosting and
IT infrastructure provisioning, `997331` licensing the right to use computer software.

## Rule 46A: invoice-cum-bill of supply
A registered person supplying both taxable and exempt goods/services to an **unregistered**
person may issue a single "invoice-cum-bill of supply".

## Rule 47: time limits
- Goods: invoice at or before removal/delivery (section 31(1)).
- Services: within **30 days** of the supply; **45 days** for insurers, banks, financial
  institutions and NBFCs.

## Rule 48: copies and e-invoicing
- Goods: triplicate, marked **ORIGINAL FOR RECIPIENT**, **DUPLICATE FOR TRANSPORTER**,
  **TRIPLICATE FOR SUPPLIER**. Services: duplicate (ORIGINAL FOR RECIPIENT, DUPLICATE FOR
  SUPPLIER). These marks don't apply to e-invoices under rule 48(4).
- Rule 48(4)/(5): notified persons must prepare invoices by uploading FORM GST INV-01 data
  to the portal and obtaining an IRN. An invoice issued otherwise "shall not be treated as
  an invoice".

## Credit and debit notes
- Use a credit note (s.34) for returns, post-sale discounts and excess tax charged. Use a
  debit note for an under-charge. Reference the original invoice number and date.
- Credit/debit notes from e-invoicing taxpayers also need IRNs.
