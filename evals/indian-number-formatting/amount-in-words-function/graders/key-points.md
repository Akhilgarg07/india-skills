---
type: llm
---

PASS only if the response does ALL of the following:
1. Uses the Indian units thousand, lakh and crore (never million/billion), so 120000 gives 'One Lakh Twenty Thousand Rupees Only'.
2. Handles paise, e.g. 1050.50 gives 'One Thousand Fifty Rupees and Fifty Paise Only' (or equivalent wording with 'Paise'), ending with 'Only'.
3. Handles amounts of a crore and above correctly (e.g. 10,00,00,000 gives 'Ten Crore', 1,00,00,00,000 gives 'One Hundred Crore').
4. Parses the string without binary floating-point errors (e.g. splits on the decimal point or uses integer paise) and handles edge cases such as zero or singular 'One Rupee'.

FAIL if the function produces 'million' or mishandles lakh (e.g. 'One Hundred Twenty Thousand').
