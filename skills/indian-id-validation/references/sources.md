# Sources: indian-id-validation

**Last verified: 2026-10-18**

Method key: **[page]** = official page/PDF downloaded and the quoted text read in full;
**[extract]** = official page could not be downloaded from our environment, fact taken
from a search-engine extract of the official URL; **[test]** = checked empirically.

## GSTIN
- [page] CBIC, CGST Rules, Chapter III Registration, rule 10: GSTIN format "two characters
  for the State code; ten characters for the PAN or the Tax Deduction and Collection
  Account Number; two characters for the entity code; and one checksum character".
  https://cbic-gst.gov.in/gst-registration-rules.html
- [page] CBIC, GST Registration flier (June 2017): "The first 2 digits of the GSTIN is the
  State code, next 10 digits are the PAN of the legal entity, the next two digits are for
  entity code, and the last digit is check sum number"; one GSTIN per state per PAN.
  https://cbic-gst.gov.in/pdf/e-version-gst-fliers/regn-GST-onlineversion-07june2017.pdf
- [page] GST state code list 01-38 (Commercial Taxes Department, Government of Nagaland).
  https://nagalandtax.nic.in/docs/GST/Statistics/GST_State_Code_List.pdf
- [extract] Codes 97 (Other Territory) and 99: GSTN e-way bill API docs state code page and
  e-invoice master codes. https://docs.ewaybillgst.gov.in/apidocs/state-code.html ,
  https://einvoice1.gst.gov.in/Others/MasterCodes
- [test] Check-character algorithm: no official publication found (TODO(verify)). Verified
  against 19 real GSTINs: Etihad Airways' own published list
  (https://www.etihad.com/en-be/legal/gst-information-india: 27AABCE6624L1ZG,
  07AABCE6624L1ZI, 29AABCE6624L1ZC, 33AABCE6624L1ZN) and GST registration data shown on
  public GSTIN lookup sites for Air India, Air India Express and InterGlobe Aviation
  (e.g. 29AABCI2726B1ZY, 29AABCA0522B1DP, 27AABCI2726B1CD). All 19 pass.

## PAN and TAN
- [extract] Income Tax Department, "How PAN is formed and how it gets its unique identity?"
  (positions, status codes, 0001-9999, alphabetic check digit).
  https://www.incometaxindia.gov.in/w/how-pan-is-formed-and-how-it-gets-its-unique-identity-
- [extract] Income Tax Department, PAN tutorial (as amended by Finance Act, 2025).
  https://incometaxindia.gov.in/Tutorials/1.Permanent%20Account%20Number%20(PAN).pdf
- [extract] Income Tax Department, "What is TAN?" (4 letters, 00001-99999, check digit; example DELM12345L).
  https://www.incometaxindia.gov.in/w/what-is-tan-

## IFSC
- [page] RBI, NEFT FAQ Q4: "11-digit code with the first 4 alpha characters representing
  the bank, and the last 6 characters representing the branch. The 5th character is 0 (zero)."
  https://www.rbi.org.in/Commonman/English/Scripts/FAQs.aspx?Id=274
- [page] RBI report on IFSC: "fifth is numeric (kept 0)".
  https://www.rbi.org.in/scripts/PublicationReportDetails.aspx?ID=695
- [page] RBI IFSC examples RBIS0NDPA01, RBIS0GWPA01 (RBI tender / IFSC details pages).
  https://m.rbi.org.in/Scripts/IFSCDetails.aspx?pkid=47841

## Mobile numbers
- [page] DoT, National Numbering Plan 2003: "N(S)N is 10-digit for both the basic as well as
  cellular mobile services". https://www.dot.gov.in/static/uploads/2026/05/9ed5f19dbf38307edc38a54377d82cd5.pdf
- [page] TRAI, Recommendations on Telecommunication Numbering, 29 May 2020, paras 2.22-2.24,
  3.2: mobile in level 9, sub-levels of 7 and 8, and a few sub-levels of 6.
  https://www.trai.gov.in/sites/default/files/2024-09/Recommendations_29052020.pdf
- Note: TRAI recommended a revised numbering plan on 6 Feb 2025
  (https://www.trai.gov.in/sites/default/files/2025-02/Recommendation_06022025.pdf); the
  10-digit mobile format is unchanged in it. Re-check if DoT notifies a new plan.

## PIN code
- [page] PIB release on the Supreme Court PIN code: "There are 9 PIN regions in the country.
  The first 8 are geographical regions and the digit 9 is reserved for the Army Postal
  Service..." https://www.pib.gov.in/newsite/PrintRelease.aspx?relid=99700&reg=48&lang=2
- [extract] All India Pincode Directory (India Post, on data.gov.in).
  https://www.data.gov.in/catalog/all-india-pincode-directory-through-webservice

## Aadhaar
- [page] UIDAI API 2.0 Error Handling document, error 998: "Aadhaar number should be 12
  digits and conform to Verhoeff algorithm." Copy hosted by NULM (Govt. of India); the
  original uidai.gov.in URL now returns 404. https://nulm.gov.in/PDF/UIDAI-APIerrorcode.pdf
- [page] UIDAI tutorial: sandbox test Aadhaar "999999990019" (fails Verhoeff [test]).
  https://uidai.gov.in/en/tutorial
- [page] Aadhaar Act 2016 (as amended), s.29. https://uidai.gov.in/images/Aadhaar_Act_2016_as_amended.pdf
- [page] Aadhaar (Sharing of Information) Regulations 2016, reg. 6.
  https://uidai.gov.in/images/The_Aadhaar_Sharing_of_information_regulation_2016.pdf
- [page] UIDAI compliance checklist for Sub-AUA/Sub-KUA, v2.0 (May 2025), controls 27-31
  (Aadhaar Data Vault, masking to last four digits).
  https://uidai.gov.in/images/Compliance_checklist_for_certifying_compliance_with_controls_that_the_Sub_AUA_SubKUA_is_required_to_have_in_place.pdf
- [extract] UIDAI, "What is Masked Aadhaar?" (first 8 digits replaced with xxxx-xxxx).
  https://uidai.gov.in/en/283-faqs/aadhaar-online-services/e-aadhaar/1887-what-is-masked-aadhaar.html

## Algorithms
- Verhoeff algorithm tables: J. Verhoeff, *Error Detecting Decimal Codes* (1969); test
  vectors 236→3 and 12345→1 as in the standard reference.
  https://en.wikipedia.org/wiki/Verhoeff_algorithm

## Open items to verify
- Official publication of the GSTIN check-character algorithm.
- Official label for GST state code 99.
