# Sources: indian-dates-and-fiscal-year

**Last verified: 2026-10-18**

Method key: **[page]** = official page/data downloaded and read; **[extract]** = search-engine extract
of an official URL; **[test]** = behaviour observed by running code.

- [extract] General Clauses Act, 1897, s.3: "financial year" shall mean the year commencing on the first
  day of April. https://www.indiacode.nic.in/bitstream/123456789/15374/1/the_general_clauses_act,_1897.pdf
- [extract] Companies Act, 2013, s.2(41) (financial year ending 31 March; proviso for holding/subsidiary/
  associate of a foreign company, with Central Government approval after the 2018 amendment).
  https://www.mca.gov.in/Ministry/pdf/CompaniesAct2013.pdf
- [page] Income Tax e-filing portal, "Objective and scope of the New Act" FAQs: Income-tax Act 2025 in force
  from 1 April 2026; "tax year" replaces "previous year" and the assessment year concept; tax year aligned
  with FY 1 April-31 March; older years continue under the 1961 Act.
  https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/objective-and-scope-new-act
- [page] e-filing portal TDS Compliance FAQs (AIS for AY 2026-27; Form 168 for Tax Year 2026-27).
  https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/tds-compliance
- [page] PIB (Department of Consumer Affairs), draft Legal Metrology (Indian Standard Time) Rules, 2025:
  "IST, based on UTC with a +5:30-hour offset, is maintained by the CSIR-National Physical Laboratory".
  https://www.pib.gov.in/PressReleasePage.aspx?PRID=2096622 . `TODO(verify)`: whether the IST Rules have
  been finalised.
- [page] CSIR-NPL / PIB flyer, "Indian Standard Time Metrology at CSIR-NPL" (IST traceable to UTC; NPL is the
  custodian). https://static.pib.gov.in/WriteReadData/userfiles/0401_IST%20Flyer-One%20page%20writeup.pdf
- [page] IANA tz database (`asia`: Zone Asia/Kolkata, +5:30 since 1945 with war time in 1942-45;
  `backward`: Link Asia/Kolkata Asia/Calcutta). https://github.com/eggert/tz
- [page] Unicode CLDR `en-IN` Gregorian date formats (`short` = `dd/MM/yy`, `medium` = `d MMM y`).
  https://github.com/unicode-org/cldr-json/blob/main/cldr-json/cldr-dates-full/main/en-IN/ca-gregorian.json
- [test] `Intl.DateTimeFormat("en-IN")` outputs and `new Date("01/04/2026")` behaviour, Node.js 22.22.0,
  2026-10-18.
- [extract] NIC e-invoice API sandbox, Generate IRN samples (`DocDtls.Dt` as "18/08/2020"; response `AckDt`
  as `yyyy-MM-dd HH:mm:ss`). https://einv-apisandbox.nic.in/version1.03/generate-irn.html
