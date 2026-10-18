# Sources: indian-number-formatting

**Last verified: 2026-10-18**

Method key: **[page]** = official page/data downloaded and read; **[test]** = behaviour observed
by running code; **[extract]** = search-engine extract of an official URL.

- [page] PIB, "Symbol for Indian Rupee approved", Cabinet decision of 15 July 2010 (inclusion in
  the Unicode Standard, ISO/IEC 10646 and IS 13194).
  https://www.pib.gov.in/newsite/erelcontent.aspx?relid=63283
- [extract] National Portal of India: Unicode Consortium encoded the symbol at U+20B9 (Unicode 6.0,
  October 2010). https://archive.india.gov.in/howdo/otherservice_details.php?service=30
- [extract] RBI currency FAQs (symbol incorporated in banknotes and coins from 2011).
  https://www.rbi.org.in/commonperson/English/Scripts/FAQs.aspx?Id=3158
- [page] Unicode CLDR `en-IN` number data: decimal `#,##,##0.###`, currency `¤#,##,##0.00`, short
  forms `0K`, `0L`, `0Cr`, `0KCr`, `0LCr`.
  https://github.com/unicode-org/cldr-json/blob/main/cldr-json/cldr-numbers-full/main/en-IN/numbers.json
- [test] `Intl.NumberFormat` outputs in references/formatting-reference.md, run on Node.js 22.22.0
  (full ICU) on 2026-10-18.
- [extract] Government of India usage of "lakh crore", e.g. DEA, *India's External Debt: A Status
  Report 2024-25* ("₹63 lakh crore").
  https://dea.gov.in/files/external_debt_documents/Ex%20Debt%20Report%202024-25_Final.pdf

Amount-in-words style ("... Rupees Only", "Rupees ... Only") is a widespread commercial convention
in India (invoices, cheques), not a statutory format. No official style guide prescribes it.
